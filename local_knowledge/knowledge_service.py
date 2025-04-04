import json
import os
import importlib.util
from typing import List, Dict, Optional, Union, Any

class KnowledgeService:
    def __init__(self, knowledge_file="knowledge.json"):
        self.knowledge_file = knowledge_file
        self.knowledge_dir = os.path.dirname(os.path.abspath(self.knowledge_file))
        if not os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)
    
    def _load_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """加载知识库文件"""
        if not os.path.exists(self.knowledge_file):
            return {}
        with open(self.knowledge_file, "r", encoding="utf-8") as f:
            try:
                knowledge_data = json.load(f)
                # 兼容处理：如果加载的是旧版列表格式，则转换为字典格式
                if isinstance(knowledge_data, list):
                    return {str(item["index"]): item for item in knowledge_data}
                return knowledge_data
            except json.JSONDecodeError:
                return {}
    
    def _save_knowledge(self, knowledge_dict: Dict[str, Dict[str, Any]]) -> None:
        """保存知识库文件"""
        with open(self.knowledge_file, "w", encoding="utf-8") as f:
            json.dump(knowledge_dict, f, ensure_ascii=False, indent=4)
    
    def query_all_knowledge(self) -> List[Dict[str, Any]]:
        """查询所有知识描述"""
        knowledge_dict = self._load_knowledge()
        descriptions = []
        for key, knowledge in knowledge_dict.items():
            descriptions.append({
                "index": knowledge["index"],
                "description": knowledge.get("description", "")
            })
        return descriptions
    
    def query_knowledge_detail(self, indices: List[int]) -> List[str]:
        """
        查询具体知识细节
        
        参数:
            indices: 知识索引列表
            
        返回:
            知识详情列表
        """
        knowledge_dict = self._load_knowledge()
        result = []
        
        for index in indices:
            index_key = str(index)
            if index_key in knowledge_dict:
                knowledge = knowledge_dict[index_key]
                detail_parts = ["# description", knowledge['description'], "# detail"]
                
                # 获取detail内容
                if knowledge.get("detail") is not None:
                    detail_parts.append(knowledge["detail"])
                
                # 获取detail_file内容
                if knowledge.get("detail_file") is not None:
                    file_path = knowledge["detail_file"]
                    # Check if file_path is an absolute path
                    if not os.path.isabs(file_path):
                        # If it's a relative path, join with the knowledge file directory
                        file_path = os.path.join(os.path.dirname(self.knowledge_file), file_path)
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                detail_parts.append(f.read())
                        except Exception as e:
                            detail_parts.append(f"Error reading file: {str(e)}")
                
                # 获取detail_script内容
                if knowledge.get("detail_script") is not None:
                    try:
                        script_path = knowledge.get("detail_script")
                        # Check if script_path is an absolute path
                        if os.path.isabs(script_path):
                            script_full_path = script_path
                        else:
                            # If it's a relative path, join with the knowledge file directory
                            script_full_path = os.path.join(os.path.dirname(self.knowledge_file), script_path)
                        
                        if os.path.exists(script_full_path):
                            spec = importlib.util.spec_from_file_location(f"script_{index}", script_full_path)
                            if spec and spec.loader:
                                module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(module)
                                if hasattr(module, "detail"):
                                    script_detail = module.detail()
                                    detail_parts.append(script_detail)
                    except Exception as e:
                        detail_parts.append(f"Error executing script: {str(e)}")
                
                # 组合所有获取到的内容
                result.append("\n\n".join(detail_parts))
            else:
                result.append(f"Knowledge with index {index} not found")
        
        return result
    
    def add_knowledge(self, 
                     description: str, 
                     detail: Optional[str] = None, 
                     detail_file: Optional[str] = None, 
                     detail_script: Optional[str] = None) -> Dict[str, Union[bool, int]]:
        """
        添加知识
        
        参数:
            description: 知识描述
            detail: 知识内容 (可选)
            detail_file: 知识文件路径 (可选)
            detail_script: 获取知识的脚本路径 (可选)
            
        返回:
            添加结果和索引
        """
        knowledge_dict = self._load_knowledge()
        
        # 获取新的索引（如果字典为空，则从0开始，否则取最大索引+1，不能取len，因为用户有可能手动删除其中的条目，导致key和len重叠）
        if knowledge_dict:
            index = max(int(idx) for idx in knowledge_dict.keys()) + 1
        else:
            index = 0
        
        new_knowledge = {
            "index": index,
            "description": description,
        }
        
        if detail is not None:
            new_knowledge["detail"] = detail
        if detail_file is not None:
            new_knowledge["detail_file"] = detail_file
        if detail_script is not None:
            new_knowledge["detail_script"] = detail_script
        
        knowledge_dict[str(index)] = new_knowledge
        self._save_knowledge(knowledge_dict)
        
        return {
            "success": True,
            "index": index
        }
    
    def update_knowledge(self, 
                        index: int, 
                        description: Optional[str] = None, 
                        detail: Optional[str] = None, 
                        detail_file: Optional[str] = None, 
                        detail_script: Optional[str] = None) -> Dict[str, bool]:
        """
        修改知识
        
        参数:
            index: 知识索引
            description: 知识描述 (可选)
            detail: 知识内容 (可选)
            detail_file: 知识文件路径 (可选)
            detail_script: 获取知识的脚本路径 (可选)
            
        返回:
            修改结果
        """
        knowledge_dict = self._load_knowledge()
        index_key = str(index)
        
        if index_key in knowledge_dict:
            # 获取已有的知识
            existing_knowledge = knowledge_dict[index_key]
            # 创建更新后的知识对象，保留索引
            updated_knowledge = {
                "index": index,
                # 如果提供了新描述则使用，否则保留原有描述
                "description": description if description is not None else existing_knowledge.get("description", ""),
            }
            
            # 更新或保留其他字段
            if detail is not None:
                updated_knowledge["detail"] = detail
            elif "detail" in existing_knowledge:
                updated_knowledge["detail"] = existing_knowledge["detail"]
                
            if detail_file is not None:
                updated_knowledge["detail_file"] = detail_file
            elif "detail_file" in existing_knowledge:
                updated_knowledge["detail_file"] = existing_knowledge["detail_file"]
                
            if detail_script is not None:
                updated_knowledge["detail_script"] = detail_script
            elif "detail_script" in existing_knowledge:
                updated_knowledge["detail_script"] = existing_knowledge["detail_script"]
            
            knowledge_dict[index_key] = updated_knowledge
            self._save_knowledge(knowledge_dict)
            
            return {"success": True}
        else:
            return {"success": False}
