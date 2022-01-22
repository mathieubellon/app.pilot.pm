<template>
<OffPanel name="UserExaminationPanel">
    <div slot="offPanelTitle">{{ userExamined.username }}</div>
    <div slot="offPanelBody">
        <Loadarium name="fetchUserExamined">
            <UserAvatar
                size="100px"
                :user="userExamined"
            />
            <p>{{ userExamined.first_name }} {{ userExamined.last_name }}</p>
            <p>{{ userExamined.email }}</p>
            <p>{{ userExamined.job }}</p>
            <p>{{ userExamined.phone }}</p>
            <p>{{ userExamined.localization }}</p>
            <p v-if="userExamined.teams">
                <span v-for="team in userExamined.teams">@{{ team.name }}</span>
            </p>
        </Loadarium>
    </div>
</OffPanel>
</template>

<script>
import { mapState, mapActions, mapGetters, mapMutations } from "vuex"
import PilotMixin from "@components/PilotMixin"

export default {
    name: "UserExaminationPanel",
    mixins: [PilotMixin],
    computed: {
        ...mapState("users", ["userExamined"]),
    },
}
</script>
