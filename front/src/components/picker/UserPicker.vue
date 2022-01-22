<template>
<div class="UserPicker">
    <div class="flex items-center">
        <VueFuse
            class="flex-grow"
            :defaultAll="true"
            :keys="['username']"
            :list="users"
            :placeholder="$t('search')"
            :threshold="0.1"
            @result="onFuseResult"
        />
    </div>

    <div class="Picker__List">
        <div
            v-for="user in filteredUsers"
            class="Picker__ElementWrapper"
        >
            <div
                v-if="loading && lastSelection == user"
                class="Picker__Loader"
            >
                <BarLoader
                    color="#3182CE"
                    :loading="true"
                    :width="100"
                    widthUnit="%"
                />
            </div>
            <UserPickerElement
                v-else
                :disabled="loading"
                :key="user.id"
                :picked="isPicked(user)"
                :user="user"
                @pick="onPick"
            />
        </div>
    </div>
</div>
</template>

<script>
import _ from "lodash"
import PilotMixin from "@components/PilotMixin"

import UserPickerElement from "./UserPickerElement.vue"
import ButtonSpinner from "@components/ButtonSpinner"

export default {
    name: "UserPicker",
    mixins: [PilotMixin],
    components: {
        UserPickerElement,
        ButtonSpinner,
    },
    props: {
        multiple: Boolean,
        users: Array,
        pickedUser: Object,
        pickedUsersId: Array,
        loading: Boolean,
    },
    data: () => ({
        filteredUsers: [],
        lastSelection: null,
    }),
    methods: {
        onFuseResult(filteredUsers) {
            this.filteredUsers = filteredUsers
        },
        onPick(user) {
            this.lastSelection = user
            if (this.multiple) {
                // Toggle value in array (https://gist.github.com/uhtred/ec64752a8e9c9b83922b3ebb36e3ac23)
                this.$emit("pick", _.xor(this.pickedUsersId, [user.id]))
            } else {
                this.$emit("pick", user)
            }
        },
        pickAll() {
            this.lastSelection = "pickAll"
            this.$emit(
                "pick",
                this.users.map((user) => user.id),
            )
        },
        unpickAll() {
            this.lastSelection = "unpickAll"
            this.$emit("pick", [])
        },
        isPicked(user) {
            if (this.multiple) {
                return _.includes(this.pickedUsersId, user.id)
            } else {
                return this.pickedUser && this.pickedUser.id == user.id
            }
        },
    },
}
</script>
