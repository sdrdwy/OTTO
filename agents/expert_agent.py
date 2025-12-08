import json
import os
from typing import Dict, List, Any
from datetime import datetime
from langchain_community.chat_models import Tongyi
from langchain_core.messages import SystemMessage
from agents.base_agent import BaseAgent


class ExpertAgent(BaseAgent):
    def __init__(self, config_path: str):
        super().__init__(config_path)
        
        # Load knowledge base if available
        self.knowledge_base = []
        kb_path = self.config.get("knowledge_base_path", "./data/knowledge_base.jsonl")
        if os.path.exists(kb_path):
            with open(kb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.knowledge_base.append(json.loads(line))
        
        # Generate curriculum based on knowledge base
        self.curriculum = self.generate_curriculum()
    
    def generate_curriculum(self):
        """Generate a curriculum based on knowledge base"""
        if not self.knowledge_base:
            return {"topics": []}
        
        topics = list(set([item.get("topic", "通用") for item in self.knowledge_base]))
        
        curriculum = {
            "topics": topics,
            "schedule": {}
        }
        
        # Create a simple schedule mapping topics to days
        for i, topic in enumerate(topics):
            day = i + 1
            curriculum["schedule"][f"day_{day}"] = {
                "topic": topic,
                "content_summary": f"关于{topic}的基础知识和应用"
            }
        
        return curriculum
    
    def teach(self, student_name: str, topic: str):
        """Teach a student on a specific topic"""
        # Find relevant knowledge in the knowledge base
        relevant_knowledge = [item for item in self.knowledge_base if item.get("topic") == topic]
        
        if not relevant_knowledge:
            # If no specific knowledge, use general knowledge
            relevant_knowledge = self.knowledge_base[:1] if self.knowledge_base else []
        
        system_prompt = f"""
        你是{self.name}，一名专业教师，人设：{self.persona}。
        你的教学风格：{self.dialogue_style}。
        
        你正在教授学生{student_name}关于"{topic}"的知识。
        相关知识内容：{relevant_knowledge}
        
        请提供清晰、专业的教学内容，使用启发式方法引导学生思考。
        """
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            teaching_content = response.content
            
            # Generate memory of teaching session
            teaching_memory = {
                "id": f"teaching_{student_name}_{topic}_{datetime.now().isoformat()}",
                "type": "teaching",
                "timestamp": str(datetime.now()),
                "content": f"向{student_name}教授了{topic}的相关知识",
                "details": {
                    "student": student_name,
                    "topic": topic,
                    "content": teaching_content
                },
                "weight": 1.5
            }
            
            self.long_term_memory.add_memory(teaching_memory)
            
            return teaching_content
        except Exception as e:
            error_msg = f"教学过程中出现错误: {e}"
            print(error_msg)
            return error_msg
    
    def answer_question(self, student_name: str, question: str):
        """Answer a student's question"""
        system_prompt = f"""
        你是{self.name}，一名专业教师，人设：{self.persona}。
        你的教学风格：{self.dialogue_style}。
        
        学生{student_name}提出了问题："{question}"
        
        请提供专业、准确的回答，结合你的知识库内容。
        """
        
        try:
            response = self.llm.invoke([SystemMessage(content=system_prompt)])
            answer = response.content
            
            # Generate memory of Q&A session
            qa_memory = {
                "id": f"qa_{student_name}_{question[:20]}_{datetime.now().isoformat()}",
                "type": "question_answer",
                "timestamp": str(datetime.now()),
                "content": f"回答了{student_name}关于'{question[:30]}...'的问题",
                "details": {
                    "student": student_name,
                    "question": question,
                    "answer": answer
                },
                "weight": 1.2
            }
            
            self.long_term_memory.add_memory(qa_memory)
            
            return answer
        except Exception as e:
            error_msg = f"回答问题时出现错误: {e}"
            print(error_msg)
            return error_msg
    
    def create_exam(self, num_questions: int = 5):
        """Create an exam based on the curriculum and knowledge base"""
        if not self.knowledge_base:
            return {"questions": []}
        
        # Sample questions from knowledge base
        exam_questions = []
        for i in range(min(num_questions, len(self.knowledge_base))):
            knowledge_item = self.knowledge_base[i % len(self.knowledge_base)]
            topic = knowledge_item.get("topic", "通用")
            content = knowledge_item.get("content", "")
            
            system_prompt = f"""
            基于以下知识点创建一道考试题：
            主题：{topic}
            内容：{content}
            
            请创建一道相关的考试题，可以是选择题、简答题或论述题。
            返回格式：{{"question": "题目内容", "type": "question_type", "topic": "{topic}"}}
            """
            
            try:
                response = self.llm.invoke([SystemMessage(content=system_prompt)])
                question_data = json.loads(response.content.strip())
                exam_questions.append(question_data)
            except:
                # Fallback question if parsing fails
                exam_questions.append({
                    "question": f"请简述关于{topic}的主要知识点",
                    "type": "short_answer",
                    "topic": topic
                })
        
        return {"questions": exam_questions}
    
    def grade_exam(self, student_name: str, answers: List[Dict], exam_questions: List[Dict]):
        """Grade a student's exam answers"""
        total_score = 0
        max_score = len(answers) * 10  # 10 points per question
        
        grading_results = []
        
        for i, (answer, question) in enumerate(zip(answers, exam_questions)):
            system_prompt = f"""
            请对以下答案进行评分：
            问题：{question['question']}
            学生答案：{answer.get('answer', '')}
            理想答案要点：{question.get('content', '基于问题内容的相关知识点')}
            
            评分标准：准确性、完整性、逻辑性
            返回格式：{{"score": 数值, "feedback": "评语", "topic": "{question['topic']}"}}，分数范围0-10
            """
            
            try:
                response = self.llm.invoke([SystemMessage(content=system_prompt)])
                grading_data = json.loads(response.content.strip())
                
                score = grading_data.get("score", 0)
                total_score += score
                
                grading_results.append({
                    "question_idx": i,
                    "score": score,
                    "feedback": grading_data.get("feedback", ""),
                    "topic": grading_data.get("topic", question.get("topic", "通用"))
                })
            except:
                # Default grading if parsing fails
                grading_results.append({
                    "question_idx": i,
                    "score": 5,  # Default to 5/10
                    "feedback": "自动评分",
                    "topic": question.get("topic", "通用")
                })
                total_score += 5
        
        overall_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Store grading memory
        grading_memory = {
            "id": f"exam_grade_{student_name}_{datetime.now().isoformat()}",
            "type": "exam_grading",
            "timestamp": str(datetime.now()),
            "content": f"{student_name}的考试成绩：{overall_score:.1f}分",
            "details": {
                "student": student_name,
                "total_score": overall_score,
                "grading_results": grading_results,
                "answers": answers
            },
            "weight": 2.0
        }
        
        self.long_term_memory.add_memory(grading_memory)
        
        return {
            "total_score": overall_score,
            "grading_results": grading_results,
            "max_score": max_score
        }