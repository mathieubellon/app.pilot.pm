<script>
import { mapState, mapMutations, mapGetters, mapActions } from "vuex"

export default {
    name: "ResponsiveMixin",
    computed: {
        ...mapState("responsive", ["viewportWidth"]),
        ...mapGetters("responsive", [
            "viewportPhone",
            "viewportTablet",
            "viewportDesktop",
            "viewportPhoneToLarge",
            "viewportLarge",

            "viewportLTEPhone",
            "viewportLTETablet",
            "viewportLTEDesktop",
            "viewportLTELarge",

            "viewportGTEPhone",
            "viewportGTETablet",
            "viewportGTEDesktop",
            "viewportGTELarge",
        ]),
    },
}
</script>
