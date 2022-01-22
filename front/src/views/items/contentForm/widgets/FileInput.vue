<template>
<div>
    <p>
        Le champ upload tel qu'il existait avant la V3 a été déprécié.
        <br />
        Il est désormais recommandé d'utiliser le panel "Fichiers liés" dans le menu de droite pour
        gérer vos médias associés au contenu.
    </p>

    <div v-if="value">
        <img :src="djangoSettings.AWS_S3_BASE_URL + value" />
        <br />
        <a
            :href="djangoSettings.AWS_S3_BASE_URL + value"
            target="_blank"
        >
            Télécharger
        </a>
    </div>
</div>
</template>

<script>
import _ from "lodash"

export default {
    name: "FileInput",
    props: ["schema", "value"],
    data: () => ({
        // Clone the top-level variables, to prevent memory leak incurred by a top-level reactive object.
        djangoSettings: _.cloneDeep(window.pilot.djangoSettings),
    }),
}
</script>
