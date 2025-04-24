import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Berichte from "@/views/Berichte.vue";
import AthletenView from "@/views/AthletenView.vue";
import TeamsView from "@/views/TeamsView.vue";
import MedaillenspiegelView from "@/views/MedaillenspiegelView.vue";
import DatenschutzView from "@/views/DatenschutzView.vue";
import ImpressumView from "@/views/ImpressumView.vue";
import HilfeView from "@/views/HilfeView.vue";
import MitwirkendeView from "@/views/MitwirkendeView.vue";
import LoginView from "@/views/LoginView.vue";
import PageNotFoundView from '@/views/PageNotFoundView.vue';
import RennstrukturanalyseEmpty from '../views/RennstrukturanalyseEmpty.vue';
import RennstrukturanalyseSingle from '../views/RennstrukturanalyseSingle.vue';
import RennstrukturanalyseMultiple from '../views/RennstrukturanalyseMultiple.vue';
import RennstrukturanalyseWrapper from '../views/RennstrukturanalyseWrapper.vue';

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
            path: '/rennstrukturanalyse',
            component: RennstrukturanalyseWrapper,
            children: [
              {
                path: '',
                name: 'rennstrukturanalyse-empty',
                component: RennstrukturanalyseEmpty
              },
              {
                path: 'single/:comp_id?/:event_id?/:race_id?',
                name: 'rennstrukturanalyse-single',
                component: RennstrukturanalyseSingle
              },
              {
                path: 'multiple',
                name: 'rennstrukturanalyse-multiple',
                component: RennstrukturanalyseMultiple
              }
            ]
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
            path: '/mitwirkende',
            name: 'mitwirkende',
            component: MitwirkendeView
        },
        {
            path: '/auth',
            name: 'Login',
            component: LoginView
        },
        {
            path: '/:catchAll(.*)',
            name: 'PageNotFound',
            component: PageNotFoundView
        }
    ]
})

export default router
