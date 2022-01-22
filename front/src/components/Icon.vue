<!--
PLEASE read doc in IconMixin.vue
-->

<script>
import IconMixin from "@components/IconMixin"

import Activity from "@svg/zap.svg"
import Asset from "@svg/paperclip.svg"
import Bell from "@svg/bell.svg"
import Calendar from "@svg/calendar.svg"
import Channel from "@svg/cast.svg"
import Check from "@svg/check.svg"
import CheckCircleHeroicon from "@svg/check_circle_heroicon.svg"
import CheckMultiple from "@svg/check_multiple.svg"
import ChevronDown from "@svg/chevron_down.svg"
import ChevronLeft from "@svg/chevron_left.svg"
import ChevronRight from "@svg/chevron_right.svg"
import ChevronUp from "@svg/chevron_up.svg"
import Close from "@svg/close.svg"
import CloseCircle from "@svg/close_circle.svg"
import Comment from "@svg/message_circle.svg"
import Copy from "@svg/copy.svg"
import Dashboard from "@svg/activity.svg"
import Download from "@svg/download.svg"
import Edit from "@svg/edit.svg"
import EmptyTasks from "@svg/empty_tasks.svg"
import Export from "@svg/export.svg"
import ExternalLink from "@svg/external_link.svg"
import Eye from "@svg/eye.svg"
import File from "@svg/file.svg"
import FileAudio from "@svg/file_audio.svg"
import FileDefault from "@svg/file_default.svg"
import FileExcel from "@svg/file_excel.svg"
import FileImage from "@svg/file_image.svg"
import FilePDF from "@svg/file_pdf.svg"
import FilePlus from "@svg/file_plus.svg"
import FilePowerpoint from "@svg/file_powerpoint.svg"
import FileVideo from "@svg/file_video.svg"
import FileWord from "@svg/file_word.svg"
import FileZIP from "@svg/file_zip.svg"
import Folder from "@svg/folder.svg"
import FolderPlus from "@svg/folder_plus.svg"
import Frown from "@svg/frown.svg"
import Hierarchy from "@svg/hierarchy.svg"
import Home from "@svg/home.svg"
import Image from "@svg/image.svg"
import Info from "@svg/info.svg"
import Item from "@svg/file.svg"
import Language from "@svg/globe.svg"
import Layers from "@svg/layers.svg"
import LockClosed from "@svg/lock_closed.svg"
import LockOpen from "@svg/lock_open.svg"
import Menu from "@svg/menu.svg"
import MenuDotsVertical from "@svg/menu_dots_vertical.svg"
import MenuDotsHorizontal from "@svg/menu_dots_horizontal.svg"
import MoveHandle from "@svg/move_handle.svg"
import Plus from "@svg/plus.svg"
import PlusCircle from "@svg/plus_circle.svg"
import Print from "@svg/printer.svg"
import Project from "@svg/folder.svg"
import ProjectClosed from "@svg/project_closed.svg"
import ProjectRejected from "@svg/project_rejected.svg"
import ProjectSuggested from "@svg/project_suggested.svg"
import QuestionMark from "@svg/question_mark.svg"
import Search from "@svg/search.svg"
import Settings from "@svg/settings.svg"
import Share from "@svg/share.svg"
import Star from "@svg/star.svg"
import Status from "@svg/flag.svg"
import TableConfig from "@svg/table_config.svg"
import Tag from "@svg/tag.svg"
import Target from "@svg/target.svg"
import Trash from "@svg/trash.svg"
import User from "@svg/user.svg"
import Users from "@svg/users.svg"
import Upload from "@svg/upload.svg"
import Wiki from "@svg/book_open.svg"

const ICONS = {
    Activity,
    Asset,
    Bell,
    Calendar,
    Channel,
    Check,
    CheckCircleHeroicon,
    CheckMultiple,
    ChevronDown,
    ChevronLeft,
    ChevronRight,
    ChevronUp,
    Close,
    CloseCircle,
    Comment,
    Copy,
    Dashboard,
    Download,
    Edit,
    EmptyTasks,
    Export,
    ExternalLink,
    Eye,
    File,
    FileAudio,
    FileDefault,
    FileExcel,
    FileImage,
    FilePDF,
    FilePlus,
    FilePowerpoint,
    FileVideo,
    FileWord,
    FileZIP,
    Folder,
    FolderPlus,
    Frown,
    Hierarchy,
    Home,
    Image,
    Info,
    Item,
    Language,
    Layers,
    LockClosed,
    LockOpen,
    Menu,
    MenuDotsHorizontal,
    MenuDotsVertical,
    MoveHandle,
    Plus,
    PlusCircle,
    Print,
    Project,
    ProjectClosed,
    ProjectRejected,
    ProjectSuggested,
    QuestionMark,
    Search,
    Settings,
    Share,
    Star,
    Status,
    TableConfig,
    Tag,
    Target,
    Trash,
    Upload,
    User,
    Users,
    Wiki,
}

export default {
    name: "Icon",
    mixins: [IconMixin],
    data: () => ({
        icons: ICONS,
    }),
}
</script>
