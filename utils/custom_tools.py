tools = [
    {
        "type": "function",
        "function": {
            "name": "take_interview",
            "description": "Starts or continues the AI-led interview. Use this tool when the current phase is 'casual_chat' or 'structured_questions'. This function handles asking and managing candidate Q&A.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_history": {
                        "type": "array",
                        "description": "List of past messages between assistant and user in Streamlit format: [{'role': 'user', 'content': ...}, {'role': 'assistant', 'content': ...}]",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["user", "assistant"]
                                },
                                "content": {
                                    "type": "string"
                                }
                            },
                            "required": ["role", "content"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["chat_history"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_candidate_performance",
            "description": "Evaluates the candidate’s answers from the structured question phase. Returns a breakdown of scores, strengths, and weaknesses. Trigger this tool when user asks for analysis, feedback, or performance review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_history": {
                        "type": "array",
                        "description": "Chat messages from the structured question phase, in Streamlit format.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["user", "assistant"]
                                },
                                "content": {
                                    "type": "string"
                                }
                            },
                            "required": ["role", "content"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["chat_history"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_final_recommendation",
            "description": "Generates the final decision report based on interview performance, resume, and JD. Use when user asks for final decision, report, verdict, recommendation, or hiring decision.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chat_history": {
                        "type": "array",
                        "description": "Full chat history covering the interview process, in Streamlit format.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "role": {
                                    "type": "string",
                                    "enum": ["user", "assistant"]
                                },
                                "content": {
                                    "type": "string"
                                }
                            },
                            "required": ["role", "content"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["chat_history"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "end_conversation",
            "description": "Ends the interview session. Trigger this when the user explicitly asks to stop, quit, or end the chat.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]
