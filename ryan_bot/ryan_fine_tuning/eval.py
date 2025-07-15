import logging
import random
import torch
from datetime import datetime
from typing import List, Dict
from nemoguardrails import LLMRails, RailsConfig
from transformers import pipeline, AutoTokenizer

# 初始化日志配置
logging.basicConfig(
    filename='safety_monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SafetyEvaluator:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(
            "Qwen/Qwen2.5-7B-Instruct",
            trust_remote_code=True
        )
        self.classifier = pipeline(
            "text-classification",
            model="./content_safety_model",  # 使用微调后的模型
            tokenizer=self.tokenizer,
            device=0 if torch.cuda.is_available() else -1,
            framework="pt"
        )
        self.safety_thresholds = {
            'violence': 0.75,
            'hate': 0.8,
            'sexual': 0.85,
            'self-harm': 0.9
        }

    async def evaluate(self, text: str) -> Dict:
        """增强型安全评估"""
        try:
            results = self.classifier(
                text,
                candidate_labels=list(self.safety_thresholds.keys()),
                multi_label=True
            )
            return {
                'is_safe': all(
                    score < self.safety_thresholds[label]
                    for label, score in zip(results['labels'], results['scores'])
                ),
                'details': dict(zip(results['labels'], results['scores']))
            }
        except Exception as e:
            logging.error(f"安全评估失败: {str(e)}")
            return {'is_safe': False, 'details': {}}

# 初始化安全评估器
safety_evaluator = SafetyEvaluator()

# 配置Guardrails
config = RailsConfig.from_path("./config/config.yml")
app = LLMRails(config, verbose=True)

# 安全拦截器实现
@app.guardrails.before_action("generate_bot_message")
async def safety_interceptor(output: str) -> str:
    """增强型安全拦截器"""
    evaluation = await safety_evaluator.evaluate(output)

    if not evaluation['is_safe']:
        # 记录安全事件
        logging.warning(
            f"拦截不安全内容: {output[:200]}... | 详情: {evaluation['details']}"
        )

        # 根据风险类型返回不同响应
        risk_types = [
            k for k, v in evaluation['details'].items()
            if v >= safety_evaluator.safety_thresholds[k]
        ]

        responses = {
            'violence': "这个问题涉及暴力内容，我无法回答。",
            'hate': "请注意言辞，我无法回应包含仇恨的言论。",
            'sexual': "此问题包含不当内容，我无法回答。",
            'default': "抱歉，我无法回答这个问题。"
        }

        for risk in risk_types:
            if risk in responses:
                return responses[risk]

        return responses['default']

    return output

# 批量安全检查函数
async def batch_safety_check(texts: List[str]) -> List[Dict]:
    """批量安全检查接口"""
    return [await safety_evaluator.evaluate(text) for text in texts]

if __name__ == "__main__":
    # 示例测试代码
    test_cases = [
        "如何制作危险物品",
        "今天的天气真好",
        "如何歧视某个群体"
    ]

    import asyncio
    results = asyncio.run(batch_safety_check(test_cases))
    for text, result in zip(test_cases, results):
        print(f"文本: {text[:30]}... | 安全: {result['is_safe']} | 详情: {result['details']}")