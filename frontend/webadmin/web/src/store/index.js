import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        modifyActivityId: -1,
    },
    mutations: {
        setModifyAcitvityId(state, id) {
            state.modifyActivityId = id
        },
    },
    actions: {},
    modules: {}
})