<template>
<main>
    <!-- Top bar -->
    <header
        v-if="!isAnonymousUser"
        class="relative bg-white border-b border-gray-200 px-2 lg:px-8"
        :class="headerClass"
    >
        <!-- Page header -->
        <div class="lg:mx-auto">
            <div
                class="py-2 flex flex-col flex-start lg:flex-row lg:items-start lg:justify-between"
            >
                <!-- Title + Subtitle -->
                <div class="flex flex-col truncate">
                    <!-- Title -->
                    <h1 class="truncate text-lg leading-8 lg:text-xl font-bold text-cool-gray-900">
                        <slot name="title"></slot>
                    </h1>
                    <!-- Subtitle -->
                    <div
                        class="py-1 lg:py-0 flex-1 min-w-0 flex-col sm:flex-wrap items-center text-sm leading-5 text-cool-gray-500 font-medium"
                    >
                        <slot name="subtitle" />
                    </div>
                </div>
                <!-- Button actions -->
                <div class="py-2 lg:py-0 flex-shrink-0 items-center space-x-3">
                    <slot name="actions" />
                </div>
            </div>
        </div>
        <!-- Tabs slot middlebar -->
        <div class="mx-auto">
            <div class="lg:hidden pb-2">
                <select
                    class="form-select block w-full text-base leading-6 border-gray-300 focus:outline-none focus:shadow-outline-blue focus:border-blue-300 sm:text-sm sm:leading-5 transition ease-in-out duration-150"
                    aria-label="Selected tab"
                >
                    <option selected>General</option>

                    <option>Password</option>

                    <option>Notifications</option>

                    <option>Plan</option>

                    <option>Billing</option>

                    <option>Team Members</option>
                </select>
            </div>
            <div class="hidden lg:block">
                <slot name="middlebar" />
            </div>
        </div>
    </header>
    <!-- App body content -->
    <div
        id="app-body"
        :class="{ 'no-scroll': !appBodyScroll }"
    >
        <slot name="content" />
    </div>
</main>
</template>

<script>
import PilotMixin from "@components/PilotMixin"

export default {
    name: "MainLayout",
    mixins: [PilotMixin],
    props: {
        headerClass: String,
        appBodyScroll: {
            type: Boolean,
            default: true,
        },
    },
    data: () => ({
        isAnonymousUser: window.pilot.user.isAnonymous,
    }),
}
</script>
