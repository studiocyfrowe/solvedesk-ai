from pydantic import BaseModel, ConfigDict

class EnvConfig(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=()
    )
    
    model_local_path: str
    chroma_dir: str
    collection_name: str