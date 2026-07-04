# def parse_answer(answer):
class AnswerParser:
    
    def parse(self, answer : str) -> dict:
        result = {
            "corrected" : "",
            "reason" : "",
            "translation" : "",
            "better" : "",
            "grammar": "",
            "vocabulary": "",
            "naturalness": "",
            "level": ""
        }

        current = None

        for line in answer.split("\n"):
            line = line.strip()

            if not line:
                continue

            if "[수정된 문장]" in line:
                current = "corrected"
                continue
            elif "[수정 이유]" in line:
                current = "reason"
                continue
            elif "[한국어 번역]" in line:
                current = "translation"
                continue
            elif "[더 좋은 표현]" in line:
                current = "better"
                continue
            elif "[AI 분석]" in line:
                current = "analysis"
                continue
            
            if current == "analysis":
                if line.startswith("Grammar"):
                    result["grammar"] = line.split(":")[1].strip()
                elif line.startswith("Vocabulary"):
                    result["vocabulary"] = line.split(":")[1].strip()
                elif line.startswith("Naturalness"):
                    result["naturalness"] = line.split(":")[1].strip()
                elif line.startswith("Level"):
                    result["level"] = line.split(":")[1].strip()
                continue
                
            if current:
                result[current] += line + "\n"
            
            for key in result:
                if isinstance(result[key], str):
                    result[key] = result[key].strip()
        
        return result   