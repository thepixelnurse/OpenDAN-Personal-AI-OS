import logging
import toml
from aios_kernel import Workflow
from package_manager import PackageEnv,PackageEnvManager,PackageMediaInfo,PackageInstallTask
from agent_manager import AgentManager
logger = logging.getLogger(__name__)
import os

class WorkflowManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WorkflowManager, cls).__new__(cls)
        return cls._instance


    def initial(self,root_dir:str) -> None:
        self.loaded_workflow = {}
        self.workflow_env = PackageEnvManager().get_env(f"{root_dir}/workflows.cfg")
        self.db_file = os.path.abspath(f"{root_dir}/workflows.db")
        if self.workflow_env is None:
            raise Exception("WorkflowManager initial failed")
        
    async def get_agent_default_workflow(self,agent_id:str) -> Workflow:
        pass

    async def get_workflow(self,workflow_id:str) -> Workflow:
        the_workflow : Workflow = self.loaded_workflow.get(workflow_id)
        if the_workflow:
            return the_workflow
        
        # try load from disk
        workflow_media_info = self.workflow_env.load(workflow_id)
        if workflow_media_info is None:
            return None
        
        the_workflow = await self._load_workflow_from_media(workflow_media_info)
        if the_workflow is None:
            logger.warn(f"load workflow {workflow_id} from media failed!")

        for v in the_workflow.role_group.roles.values():
            agent = await AgentManager().get(v.agent_name)
            if agent is None:
                logger.error(f"load agent {v.agent_name} failed!")
                return None
            v.agent = agent


        return the_workflow
    
    async def _load_workflow_from_media(self,workflow_media:PackageMediaInfo) -> Workflow:
        reader = self.workflow_env._create_media_loader(workflow_media)
        if reader is None:
            logger.error(f"create media loader for {workflow_media} failed!")
            return None
        
        try:
            config_file = await reader.read("workflow.toml","r")
            if config_file is None:
                logger.error(f"read workflow config from {workflow_media} failed!")
                return None

            config_data = await config_file.read()
            config = toml.loads(config_data)
            result_workflow = Workflow()
            if result_workflow.load_from_config(config) is False:
                logger.error(f"load workflow from {workflow_media} failed!")
                return None
            result_workflow.db_file = self.db_file
            return result_workflow
        except Exception as e:
            logger.error(f"read workflow.toml cfg from {workflow_media} failed! unexpected error occurred: {str(e)}")
            return None