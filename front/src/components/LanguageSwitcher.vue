<template>
<form
    v-if="isAnonymousUser"
    :action="urls.i18nSetlang"
    method="post"
>
    <input
        name="csrfmiddlewaretoken"
        type="hidden"
        :value="csrfToken"
    />
    <template v-if="currentLocale == 'fr'">
        <input
            name="language"
            type="hidden"
            value="en"
        />
        <input
            class="button is-white is-small"
            type="submit"
            value="English"
        />
    </template>
    <template v-else>
        <input
            name="language"
            type="hidden"
            value="fr"
        />
        <input
            class="button is-white is-small"
            type="submit"
            value="Français"
        />
    </template>
</form>
</template>

<script>
import urls from "@js/urls"
import { csrfToken } from "@js/ajax"

export default {
    name: "LanguageSwitcher",
    data: () => ({
        urls,
        csrfToken,
        currentLocale: window.pilot.currentLocale,
        isAnonymousUser: window.pilot.user.isAnonymous,
    }),
}
</script>
