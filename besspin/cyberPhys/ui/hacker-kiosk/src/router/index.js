import Vue from 'vue'
import Router from 'vue-router'
import Hack01_Start from '@/components/Hack01_Start'
import Hack02_Intro from '@/components/Hack02_Intro'
import Hack03_Show from '@/components/Hack03_Show'
import Hack04_Access from '@/components/Hack04_Access'
import Hack05_InfoAttempt from '@/components/Hack05_InfoAttempt'
import Hack06_InfoExploit from '@/components/Hack06_InfoExploit'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'hack01_start',
      component: Hack01_Start
    },
    {
      path: '/hack02_intro',
      name: 'hack02_intro',
      component: Hack02_Intro
    },
    {
      path: '/hack03_show',
      name: 'hack03_show',
      component: Hack03_Show
    },
    {
      path: '/hack04_access',
      name: 'hack04_access',
      component: Hack04_Access
    },

    {
      path: '/hack05_info_attempt',
      name: 'hack05_info_attempt',
      component: Hack05_InfoAttempt
    },
    {
      path: '/hack06_info_exploit',
      name: 'hack06_info_exploit',
      component: Hack06_InfoExploit
    },
    {
      path: '/hack07_critical_attempt',
      name: 'hack07_critical_attempt',
      component: Hack07_CriticalAttempt
    },
    {
      path: '/hack08_critical_exploit',
      name: 'hack08_critical_exploit',
      component: Hack08_CriticalExploit
    },

    {
      path: '/hack09_protect',
      name: 'hack09_protect',
      component: Hack09_Protect
    },
    {
      path: '/hack10_protect_info_attempt',
      name: 'hack10_protect_info_attempt',
      component: Hack10_ProtectInfoAttempt
    },
    {
      path: '/hack11_protect_info_stop',
      name: 'hack11_protect_info_stop',
      component: Hack11_ProtectInfoStop
    },
    {
      path: '/hack12_protect_critical',
      name: 'hack12_protect_critical',
      component: Hack12_ProtectCritical
    },
    {
      path: '/hack13_protect_critical_stop',
      name: 'hack13_protect_critical_stop',
      component: Hack13_ProtectCriticalStop
    },
    {
      path: '/hack14_existential',
      name: 'hack14_existential',
      component: Hack14_Existential
    },
    {
      path: '/hack15_solution',
      name: 'hack15_solution',
      component: Hack15_Solution
    },
  ]
})