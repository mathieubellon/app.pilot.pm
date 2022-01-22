<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"

export default {
    name: "TileMixin",
    props: {
        tileIndex: Number,
        tile: Object,
    },
    data: () => ({
        transition: "animated fadeInRight",
        tileList: [],
        num_pages: null,
        next_page: null,
        previous_page: null,
    }),
    computed: {
        currentPage() {
            return this.next_page === null ? this.num_pages : this.next_page - 1
        },
    },
    methods: {
        ...mapActions("dashboard", ["removeTileFromUserTiles"]),
    },
}
</script>

<style lang="scss">
@import "~@sass/colors.scss";

.DashboardTile {
    @apply flex flex-col bg-white rounded border border-gray-200 mr-2 mb-5 p-5;
    width: 100%;
    height: 500px;
}
.DashboardTile__pagination {
    @apply flex justify-between items-center mt-3;
}
.DashboardTile__remove {
    @apply bg-orange-200 text-orange-500 rounded;
    font-size: 0.8em;
    font-weight: 500;
}

.DashboardTile__header {
    @apply text-base font-bold mb-2 flex justify-between items-center;
}

.DashboardTile__body {
    @apply flex-grow h-auto overflow-auto;
}

.DashboardTile__body__empty {
    @apply flex flex-grow h-full items-center justify-center bg-gray-100 rounded;
}
</style>
