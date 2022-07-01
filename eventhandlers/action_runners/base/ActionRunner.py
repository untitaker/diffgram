from shared.database.action.action import Action
from shared.queueclient.QueueClient import QueueClient, RoutingKeys, Exchanges
from shared.database.event.event import Event
from shared.regular import regular_log
from shared.helpers import sessionMaker
from shared.database.action.action_template import Action_Template
from shared.shared_logger import get_shared_logger
from shared.database.action.action_run import ActionRun
from sqlalchemy.orm.session import Session
from eventhandlers.action_runners.base.ActionTrigger import ActionTrigger
from eventhandlers.action_runners.base.ActionCondition import ActionCondition
from eventhandlers.action_runners.base.ActionCompleteCondition import ActionCompleteCondition
from shared.data_tools_core import Data_tools

logger = get_shared_logger()

data_tools = Data_tools().data_tools

class ActionRegistrationError(Exception):
    pass


class ActionRunner:
    action: Action
    event_data: dict
    log: dict
    public_name: str
    icon: str
    kind: str
    category: str
    description: str
    trigger_data: ActionTrigger
    condition_data: ActionCondition
    completion_condition_data: ActionCompleteCondition
    action_run: ActionRun

    def __init__(self, action = None, event_data: dict = None):
        self.action = action
        self.event_data = event_data
        self.log = regular_log.default()
        self.mngr = QueueClient()

    def save_html_output(self, session, html_data: str):
        self.action.output = {'html': html_data}
        self.action_run.output = {'html': html_data}
        session.add(self.action)
        session.add(self.action_run)

    def execute_pre_conditions(self, session: Session) -> bool:
        raise NotImplementedError

    def execute_action(self, session: Session) -> None:
        raise NotImplementedError

    def verify_registration_data(self) -> None:
        fields = ['public_name',
                  'description',
                  'icon',
                  'kind',
                  'trigger_data',
                  'condition_data',
                  'completion_condition_data']
        for field in fields:
            if self.__getattribute__(field) is None:
                msg = f'Error registering {self.__class__}. Provide {field}'
                logger.error(msg)
                raise ActionRegistrationError(msg)

    def update(self, session) -> None:
        self.verify_registration_data()
        payload = {
            "public_name": self.public_name,
            "description": self.description,
            "trigger_data": self.trigger_data.build_data(),
            "condition_data": self.condition_data.build_data(),
            "completion_condition_data": self.completion_condition_data.build_data(),
            "icon": self.icon,
            "category": None
        }
        Action_Template.update_by_kind(session, self.kind, payload)

    def register(self, session) -> None:
        self.verify_registration_data()
        Action_Template.register(
            session = session,
            public_name = self.public_name,
            description = self.description,
            icon = self.icon,
            kind = self.kind,
            category = None,
            trigger_data = self.trigger_data.build_data() if self.trigger_data else None,
            condition_data = self.condition_data.build_data() if self.condition_data else None,
            completion_condition_data = self.completion_condition_data.build_data() if self.completion_condition_data else None,
        )

    def run(self) -> None:
        with sessionMaker.session_scope_threaded() as session:
            self.action_run = ActionRun.new(
                session = session,
                workflow_id = self.action.workflow_id,
                action_id = self.action.id,
                project_id = self.action.project_id,
                workflow_run_id = None,
                file_id = None
            )

            allow = self.execute_pre_conditions(session)
            if not allow:
                return
            success = self.execute_action(session)
            if success:
                if isinstance(success, dict):
                    self.action_run.output = success

                self.declare_action_complete(session)
            else:
                self.declare_action_failed(session)

    def declare_action_failed(self, session: Session) -> None:

        event = Event.new(
            session = session,
            action_id = self.action.id,
            kind = 'action_failed',
            project_id = self.action.project_id,

        )
        event_data = event.serialize()
        self.mngr.send_message(message = event_data,
                               exchange = Exchanges.actions.value,
                               routing_key = RoutingKeys.action_trigger_event_new.value)

    def declare_action_complete(self, session: Session) -> None:
        event = Event.new(
            session = session,
            action_id = self.action.id,
            kind = 'action_completed',
            project_id = self.action.project_id,

        )
        event_data = event.serialize()
        self.mngr.send_message(message = event_data,
                               exchange = Exchanges.actions.value,
                               routing_key = RoutingKeys.action_trigger_event_new.value)