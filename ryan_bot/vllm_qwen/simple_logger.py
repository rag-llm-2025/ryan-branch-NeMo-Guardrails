class RyanLogger:
    @staticmethod
    def info(msg):
        print(f"\033[93m{msg}\033[0m")

    @staticmethod
    def warning(msg):
        print(f"\033[93m{msg}\033[0m")

    @staticmethod
    def debug(msg):
        print(f"{msg}")

    @staticmethod
    def error(msg):
        print(f"\033[31m{msg}\033[0m")

    @staticmethod
    def fatal(msg):
        print(f"\033[31m{msg}\033[0m")

    @staticmethod
    def critical(msg):
        print(f"\033[31m{msg}\033[0m")