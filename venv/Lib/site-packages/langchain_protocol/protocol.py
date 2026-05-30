# compiled with https://www.npmjs.com/package/cddl2py v0.2.2

from __future__ import annotations

from typing import Annotated, Any, Literal, Union
from typing_extensions import NotRequired, TypedDict

JsInt = int

JsUint = int

Namespace = list[str]

Extensible = dict[str, Any]

Timestamp = int

MetadataScalar = Union[None, bool, int, float, str]

MessageRole = Union[Literal["ai"], Literal["human"], Literal["system"]]

class MessageMetadata(TypedDict, extra_items=MetadataScalar):
    provider: NotRequired[str]
    model: NotRequired[str]
    model_type: NotRequired[str]
    run_id: NotRequired[str]
    thread_id: NotRequired[str]
    system_fingerprint: NotRequired[str]
    service_tier: NotRequired[str]

class TextContentBlock(TypedDict):
    type: Literal["text"]
    text: str
    id: NotRequired[str]
    index: NotRequired[BlockIndex]
    annotations: NotRequired[list[Annotation]]

class InvalidToolCall(TypedDict):
    type: Literal["invalid_tool_call"]
    id: Union[str, None]
    name: Union[str, None]
    args: Union[str, None]
    error: Union[str, None]
    index: NotRequired[BlockIndex]

class ReasoningContentBlock(TypedDict):
    type: Literal["reasoning"]
    reasoning: NotRequired[str]
    id: NotRequired[str]
    index: NotRequired[BlockIndex]

class NonStandardContentBlock(TypedDict):
    type: Literal["non_standard"]
    value: dict[str, Any]
    id: NotRequired[str]
    index: NotRequired[BlockIndex]

class ImageContentBlock(TypedDict):
    type: Literal["image"]
    id: NotRequired[str]
    file_id: NotRequired[str]
    url: NotRequired[str]
    base64: NotRequired[str]  # Base64-encoded image data
    mime_type: NotRequired[str]
    index: NotRequired[BlockIndex]

class VideoContentBlock(TypedDict):
    type: Literal["video"]
    id: NotRequired[str]
    file_id: NotRequired[str]
    url: NotRequired[str]
    base64: NotRequired[str]  # Base64-encoded video data
    mime_type: NotRequired[str]
    index: NotRequired[BlockIndex]

class AudioContentBlock(TypedDict):
    type: Literal["audio"]
    id: NotRequired[str]
    file_id: NotRequired[str]
    url: NotRequired[str]
    base64: NotRequired[str]  # Base64-encoded audio data
    mime_type: NotRequired[str]
    index: NotRequired[BlockIndex]

class FileContentBlock(TypedDict):
    type: Literal["file"]
    id: NotRequired[str]
    file_id: NotRequired[str]
    url: NotRequired[str]
    base64: NotRequired[str]  # Base64-encoded file data
    mime_type: NotRequired[str]
    index: NotRequired[BlockIndex]

DataContentBlock = Union[ImageContentBlock, VideoContentBlock, AudioContentBlock, FileContentBlock]

class ToolCall(TypedDict):
    type: Literal["tool_call"]
    id: Union[str, None]
    name: str
    args: dict[str, Any]
    index: NotRequired[BlockIndex]

class ToolCallChunk(TypedDict):
    type: Literal["tool_call_chunk"]
    id: Union[str, None]
    name: Union[str, None]
    args: Union[str, None]  # Partial JSON string
    index: NotRequired[BlockIndex]

class ServerToolCall(TypedDict):
    type: Literal["server_tool_call"]
    id: str
    name: str
    args: dict[str, Any]
    index: NotRequired[BlockIndex]

class ServerToolCallChunk(TypedDict):
    type: Literal["server_tool_call_chunk"]
    id: NotRequired[str]
    name: NotRequired[str]
    args: NotRequired[str]
    index: NotRequired[BlockIndex]

class ServerToolResult(TypedDict):
    type: Literal["server_tool_result"]
    tool_call_id: str
    status: Union[Literal["success"], Literal["error"]]
    id: NotRequired[str]
    output: NotRequired[Any]
    index: NotRequired[BlockIndex]

ToolContentBlock = Union[ToolCall, ToolCallChunk, ServerToolCall, ServerToolCallChunk, ServerToolResult]

ContentBlock = Union[TextContentBlock, InvalidToolCall, ReasoningContentBlock, NonStandardContentBlock, DataContentBlock, ToolContentBlock]

FinalizedContentBlock = Union[TextContentBlock, ReasoningContentBlock, ToolCall, InvalidToolCall, ServerToolCall, ServerToolResult, DataContentBlock, NonStandardContentBlock]

BlockIndex = Union[JsInt, str]

class Citation(TypedDict):
    type: Literal["citation"]
    id: NotRequired[str]
    url: NotRequired[str]
    title: NotRequired[str]
    start_index: NotRequired[int]
    end_index: NotRequired[int]
    cited_text: NotRequired[str]

class NonStandardAnnotation(TypedDict):
    type: Literal["non_standard_annotation"]
    id: NotRequired[str]
    value: dict[str, Any]

Annotation = Union[Citation, NonStandardAnnotation]

class TextDelta(TypedDict):
    type: Literal["text-delta"]
    text: str

class ReasoningDelta(TypedDict):
    type: Literal["reasoning-delta"]
    reasoning: str

class DataDelta(TypedDict):
    type: Literal["data-delta"]
    data: str  # Encoded data chunk to append
    encoding: NotRequired[Literal["base64"]]  # Defaults to base64 when absent

class BlockDeltaFields(TypedDict, extra_items=Any):
    type: str

class BlockDelta(TypedDict):
    type: Literal["block-delta"]
    fields: BlockDeltaFields

ContentBlockDelta = Union[TextDelta, ReasoningDelta, DataDelta, BlockDelta]

class RunStart(TypedDict):
    method: Literal["run.start"]
    params: RunStartParams

class SubscriptionSubscribe(TypedDict):
    method: Literal["subscription.subscribe"]
    params: SubscribeParams

class SubscriptionUnsubscribe(TypedDict):
    method: Literal["subscription.unsubscribe"]
    params: UnsubscribeParams

class SubscriptionReconnect(TypedDict):
    method: Literal["subscription.reconnect"]
    params: ReconnectParams

SubscriptionCommand = Union[SubscriptionSubscribe, SubscriptionUnsubscribe, SubscriptionReconnect]

class AgentGetTree(TypedDict):
    method: Literal["agent.getTree"]
    params: AgentGetTreeParams

class InputRespond(TypedDict):
    method: Literal["input.respond"]
    params: InputRespondParams

class InputInject(TypedDict):
    method: Literal["input.inject"]
    params: InputInjectParams

InputCommand = Union[InputRespond, InputInject]

class StateGet(TypedDict):
    method: Literal["state.get"]
    params: StateGetParams

class StateListCheckpoints(TypedDict):
    method: Literal["state.listCheckpoints"]
    params: ListCheckpointsParams

class StateFork(TypedDict):
    method: Literal["state.fork"]
    params: StateForkParams

StateCommand = Union[StateGet, StateListCheckpoints, StateFork]

class _CommandFields(TypedDict):
    id: JsUint

class _CommandVariant1(_CommandFields, SubscriptionSubscribe):
    pass

class _CommandVariant2(_CommandFields, SubscriptionUnsubscribe):
    pass

class _CommandVariant3(_CommandFields, SubscriptionReconnect):
    pass

class _CommandVariant5(_CommandFields, InputRespond):
    pass

class _CommandVariant6(_CommandFields, InputInject):
    pass

class _CommandVariant7(_CommandFields, StateGet):
    pass

class _CommandVariant8(_CommandFields, StateListCheckpoints):
    pass

class _CommandVariant9(_CommandFields, StateFork):
    pass

class CommandResponse(TypedDict):
    type: Literal["success"]
    id: JsUint
    result: ResultData
    meta: NotRequired[ResponseMeta]

class ErrorResponse(TypedDict):
    type: Literal["error"]
    id: Union[JsUint, None]
    error: ErrorCode
    message: str
    stacktrace: NotRequired[str]
    meta: NotRequired[ResponseMeta]

class LifecycleEvent(TypedDict):
    method: Literal["lifecycle"]
    params: dict[str, Any]

class MessagesEvent(TypedDict):
    method: Literal["messages"]
    params: dict[str, Any]

class ToolsEvent(TypedDict):
    method: Literal["tools"]
    params: dict[str, Any]

class InputEvent(TypedDict):
    method: Literal["input.requested"]
    params: dict[str, Any]

class ValuesEvent(TypedDict):
    method: Literal["values"]
    params: dict[str, Any]

class UpdatesEvent(TypedDict):
    method: Literal["updates"]
    params: dict[str, Any]

class CheckpointsEvent(TypedDict):
    method: Literal["checkpoints"]
    params: dict[str, Any]

class CustomEvent(TypedDict):
    method: Literal["custom"]
    params: dict[str, Any]

class TasksEvent(TypedDict):
    method: Literal["tasks"]
    params: dict[str, Any]

EventData = Union[LifecycleEvent, MessagesEvent, ToolsEvent, InputEvent, ValuesEvent, UpdatesEvent, CheckpointsEvent, CustomEvent, TasksEvent]

class _EventFields(TypedDict):
    type: Literal["event"]
    event_id: NotRequired[str]  # Unique ID for reconnection (maps to SSE id:)
    seq: NotRequired[JsUint]  # Monotonic sequence number for ordering

class _EventVariant0(_EventFields, LifecycleEvent):
    pass

class _EventVariant1(_EventFields, MessagesEvent):
    pass

class _EventVariant2(_EventFields, ToolsEvent):
    pass

class _EventVariant3(_EventFields, InputEvent):
    pass

class _EventVariant4(_EventFields, ValuesEvent):
    pass

class _EventVariant5(_EventFields, UpdatesEvent):
    pass

class _EventVariant6(_EventFields, CheckpointsEvent):
    pass

class _EventVariant7(_EventFields, CustomEvent):
    pass

class _EventVariant8(_EventFields, TasksEvent):
    pass

Event = Union[_EventVariant0, _EventVariant1, _EventVariant2, _EventVariant3, _EventVariant4, _EventVariant5, _EventVariant6, _EventVariant7, _EventVariant8]

Message = Union[CommandResponse, ErrorResponse, Event]

class RunResult(TypedDict):
    run_id: NotRequired[str]  # ID of the started or resumed run

class SubscribeResult(TypedDict):
    subscription_id: str
    replayed_events: NotRequired[int]  # Events replayed from buffer

class ReconnectResult(TypedDict):
    restored: bool
    missed_events: NotRequired[int]
    current_namespaces: NotRequired[list[AgentStatusEntry]]

class EmptyResult(TypedDict):
    pass

class AgentResult(TypedDict):
    tree: AgentTreeNode

class StateGetResult(TypedDict):
    values: dict[str, Any]
    checkpoint: NotRequired[CheckpointRef]

class ListCheckpointsResult(TypedDict):
    checkpoints: list[CheckpointSummary]

class StateForkResult(TypedDict):
    run_id: str
    thread_id: str

ErrorCode = Union[Literal["invalid_argument"], Literal["unknown_command"], Literal["unknown_error"], Literal["no_such_run"], Literal["no_such_subscription"], Literal["no_such_namespace"], Literal["no_such_interrupt"], Literal["no_such_checkpoint"], Literal["permission_denied"], Literal["not_supported"]]

class ResponseMeta(TypedDict):
    applied_through_seq: NotRequired[JsUint]

RunCommand = RunStart

class _CommandVariant0(_CommandFields, RunCommand):
    pass

class RunStartParams(TypedDict):
    assistant_id: str  # Deployed graph/agent to run
    input: Any  # Graph input, resume value, or injected message
    config: NotRequired[dict[str, Any]]  # Per-run config overrides
    metadata: NotRequired[dict[str, Any]]  # Per-run metadata

Channel = Union[Literal["values"], Literal["updates"], Literal["messages"], Literal["tools"], Literal["lifecycle"], Literal["input"], Literal["checkpoints"], Literal["tasks"], Literal["custom"], Annotated[str, "custom:.+"]]

class EventStreamRequest(TypedDict):
    channels: list[Channel]
    namespaces: NotRequired[list[Namespace]]  # Prefix-match these namespace paths
    depth: NotRequired[int]  # Max depth below namespace prefix
    since: NotRequired[JsUint]  # Replay events after this seq number

class SubscribeParams(TypedDict):
    channels: list[Channel]
    namespaces: NotRequired[list[Namespace]]  # Prefix-match these namespace paths
    depth: NotRequired[int]  # Max depth below namespace prefix

class UnsubscribeParams(TypedDict):
    subscription_id: str

class ReconnectParams(TypedDict):
    run_id: str
    last_event_id: NotRequired[str]  # Last event the client processed
    subscriptions: NotRequired[list[str]]  # Subscription IDs to restore

class AgentStatusEntry(TypedDict):
    namespace: Namespace
    status: AgentStatus

SubscriptionResult = Union[SubscribeResult, ReconnectResult, EmptyResult]

AgentCommand = AgentGetTree

CommandData = Union[RunCommand, SubscriptionCommand, AgentCommand, InputCommand, StateCommand]

class _CommandVariant4(_CommandFields, AgentCommand):
    pass

Command = Union[_CommandVariant0, _CommandVariant1, _CommandVariant2, _CommandVariant3, _CommandVariant4, _CommandVariant5, _CommandVariant6, _CommandVariant7, _CommandVariant8, _CommandVariant9]

class AgentGetTreeParams(TypedDict):
    run_id: NotRequired[str]

class AgentTreeNode(TypedDict):
    namespace: Namespace
    status: AgentStatus
    graph_name: str
    children: NotRequired[list[AgentTreeNode]]
    metadata: NotRequired[dict[str, Any]]

AgentStatus = Union[Literal["started"], Literal["running"], Literal["completed"], Literal["failed"], Literal["interrupted"]]

class LifecycleCauseToolCall(TypedDict):
    type: Literal["toolCall"]  # The `tool_call_id` from the originating `tool-started` event
    tool_call_id: str

class LifecycleCauseSend(TypedDict):
    type: Literal["send"]  # Name of the parent node that issued the `Send`. Multiple Sends
    from_node: str

class LifecycleCauseEdge(TypedDict):
    type: Literal["edge"]  # Name of the parent node the edge originated from.
    from_node: str

LifecycleCause = Union[LifecycleCauseToolCall, LifecycleCauseSend, LifecycleCauseEdge]

class LifecycleData(TypedDict):
    event: AgentStatus
    graph_name: NotRequired[str]
    cause: NotRequired[LifecycleCause]  # Causation edge (see LifecycleCause)
    error: NotRequired[str]
    checkpoint: NotRequired[CheckpointRef]  # Checkpoint reference for time-travel

class MessageStartData(TypedDict):
    event: Literal["message-start"]
    role: MessageRole  # Author role for this message
    id: str  # Unique ID for this message
    metadata: NotRequired[MessageMetadata]  # Concise provider/model metadata for AI messages

class ContentBlockStartData(TypedDict):
    event: Literal["content-block-start"]
    index: int  # Positional index within the message
    content: ContentBlock

class ContentBlockDeltaData(TypedDict):
    event: Literal["content-block-delta"]
    index: int
    delta: ContentBlockDelta

class ContentBlockFinishData(TypedDict):
    event: Literal["content-block-finish"]
    index: int
    content: FinalizedContentBlock

class MessageFinishData(TypedDict):
    event: Literal["message-finish"]
    usage: NotRequired[UsageInfo]  # Token usage for AI-authored messages

class MessageErrorData(TypedDict):
    event: Literal["error"]
    message: str
    code: NotRequired[str]

MessagesData = Union[MessageStartData, ContentBlockStartData, ContentBlockDeltaData, ContentBlockFinishData, MessageFinishData, MessageErrorData]

class UsageInfo(TypedDict):
    input_tokens: NotRequired[int]
    output_tokens: NotRequired[int]
    total_tokens: NotRequired[int]

class ToolStartedData(TypedDict):
    event: Literal["tool-started"]
    tool_call_id: str
    tool_name: str
    input: NotRequired[Any]  # Tool input arguments

class ToolOutputDeltaData(TypedDict):
    event: Literal["tool-output-delta"]
    tool_call_id: str
    delta: str

class ToolFinishedData(TypedDict):
    event: Literal["tool-finished"]
    tool_call_id: str
    output: Any

class ToolErrorData(TypedDict):
    event: Literal["tool-error"]
    tool_call_id: str
    message: str
    code: NotRequired[str]

ToolsData = Union[ToolStartedData, ToolOutputDeltaData, ToolFinishedData, ToolErrorData]

class InputRespondParams(TypedDict):
    namespace: Namespace
    interrupt_id: str
    response: Any

class InputInjectParams(TypedDict):
    namespace: Namespace
    message: InputMessage

class InputMessage(TypedDict):
    role: Union[Literal["user"], Literal["system"]]
    content: str
    name: NotRequired[str]

InputResult = EmptyResult

class InputRequestedData(TypedDict):
    interrupt_id: str  # Correlates this request with input.respond
    payload: Any  # Opaque interrupt value from runtime; application-defined shape

class StateGetParams(TypedDict):
    namespace: Namespace
    keys: NotRequired[list[str]]  # Specific state keys, or omit for all

class ListCheckpointsParams(TypedDict):
    namespace: NotRequired[Namespace]
    limit: NotRequired[int]
    before: NotRequired[str]  # Cursor for pagination

class CheckpointSummary(TypedDict):
    id: str
    timestamp: str  # ISO 8601
    step: int
    node_name: NotRequired[str]  # Node that produced this checkpoint
    metadata: NotRequired[dict[str, Any]]

class CheckpointRef(TypedDict):
    id: str
    ns: NotRequired[str]

class StateForkParams(TypedDict):
    checkpoint_id: str
    input: NotRequired[Any]  # Input for the forked run
    config: NotRequired[dict[str, Any]]  # Config overrides

StateResult = Union[StateGetResult, ListCheckpointsResult, StateForkResult, EmptyResult]

ResultData = Union[RunResult, SubscriptionResult, AgentResult, InputResult, StateResult, EmptyResult]

class Checkpoint(TypedDict):
    id: str  # Fork target: pass to state.fork / configurable.checkpoint_id
    parent_id: NotRequired[str]  # Parent checkpoint id for tree linkage
    step: int  # Superstep number (-1 for first input, 0 for first loop step, ...)
    source: CheckpointSource  # Origin of the checkpoint

CheckpointSource = Union[Literal["input"], Literal["loop"], Literal["update"], Literal["fork"]]

class UpdatesData(TypedDict):
    node: NotRequired[str]  # Graph node that produced this update
    values: dict[str, Any]  # State delta

class CustomData(TypedDict):
    name: NotRequired[str]  # Custom event name for dispatch
    payload: Any  # User-defined payload

