import axios from 'axios'

export function getActivity(success, fail) {
    axios.get('/api/activities/list', {

    }).then(res => {
        if (res.status === 200) {
            let list = res.data.ActivityList
            success(list)
        } else {
            fail()
        }
    }).catch(e => {
        alert(e)
        fail()
    })
}

export function addNewActivity(form, success, fail) {
    axios.post('/api/activities/postactivity', {
        name: form.name,
        location: form.location,
        city: form.city,
        totalNum: form.totalNum,
        startdate: form.startdate,
        starttime: form.starttime,
        enddate: form.enddate,
        endtime: form.endtime,
        tag: form.tag,
        desc: form.desc
    }).then(res => {
        if (res.status === 200) {
            success()
        } else {
            fail()
        }
    }).catch(function (e) {
        alert(e)
        fail()
    })
}

export function login(form, success, fail) {
    axios.post('/api/manager/login', {
        username: form.username,
        password: form.password
    }).then(res => {
        if (res.status === 200) {
            success()
        } else {
            fail()
        }
    }).catch(function (e) {
        alert(e)
        fail()
    })
}

export function newAnnounce(announce, success, fail) {
    axios.post('api/messages/post', {
        activity_id: announce.activity_id,
        title: announce.title,
        content: announce.content
    }).then(res => {
        if (res.status === 200) {
            success()
        } else {
            fail()
        }
    }).catch(e => {
        alert(e)
        fail()
    })
}

export function editAnnounce(announce, success, fail) {
    axios.post('/api/messages/edit', {
        id: announce.id,
        title: announce.title,
        content: announce.content
    }).then(res => {
        if (res.status === 200) {
            success()
        } else {
            fail()
        }
    }).catch(e => {
        alert(e)
        fail()
    })
}

export function getAnnounceList(id, success, fail) {
    axios.post('/api/messages/list', {
        activity_id: id
    }).then(res => {
        if (res.status === 200) {
            let list = res.data.messages
            success(list)
        } else {
            fail()
        }
    }).catch(e => {
        alert(e)
        fail()
    })
}

export function deleteAnnounce(id_, success, fail) {
    axios.post('/api/messages/delete', {
        id: id_
    }).then(res => {
        if (res.status === 200) {
            success()
        } else {
            fail()
        }
    }).catch(e => {
        alert(e)
        fail()
    })
}

export function getParticipant(id_, success, fail) {
    axios.post('', {
        id: id_
    }).then(res => {
        if (res.status === 200) {
            let list = res.data.list
            success(list)
        } else {
            fail()
        }
    }).catch(e => {
        alert(e)
        fail()
    })
}