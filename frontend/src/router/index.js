import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Berichte from "@/views/Berichte.vue";
import Rennstrukturanalyse from "@/views/Rennstrukturanalyse.vue";
import AthletenView from "@/views/AthletenView.vue";
import TeamsView from "@/views/TeamsView.vue";
import MedaillenspiegelView from "@/views/MedaillenspiegelView.vue";
import DatenschutzView from "@/views/DatenschutzView.vue";
import ImpressumView from "@/views/ImpressumView.vue";
import HilfeView from "@/views/HilfeView.vue";
import LoginView from "@/views/LoginView.vue";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView
        },
        {
            path: '/berichte',
            name: 'berichte',
            component: Berichte
        },
        {
            path: '/rennstrukturanalyse/:comp_id?/:event_id?/:race_id?',
            name: 'rennstrukturanalyse',
            component: Rennstrukturanalyse
        },
        {
            path: '/athleten',
            name: 'athleten',
            component: AthletenView
        },
        {
            path: '/teams',
            name: 'teams',
            component: TeamsView
        },
        {
            path: '/medaillenspiegel',
            name: 'medaillenspiegel',
            component: MedaillenspiegelView
        },
        {
            path: '/datenschutz',
            name: 'datenschutz',
            component: DatenschutzView
        },
        {
            path: '/impressum',
            name: 'impressum',
            component: ImpressumView
        },
        {
            path: '/hilfe',
            name: 'hilfe',
            component: HilfeView
        },
        {
            path: '/auth',
            name: 'Login',
            component: LoginView
        },
    ]
})

export default router
