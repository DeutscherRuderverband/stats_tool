import router from '../router'
import axios from "axios";

axios.interceptors.response.use(
    function (response) {
        return response
    }, function (error) {
        console.log(error.response.data)
        if (error.response.status === 401) {
            let path = window.location.pathname;
            path = path.replace(`\[/auth?redirect=\]+`,'');
            const searchParameter = window.location.search;
            localStorage.setItem('session_token', '')
            router.push(`/auth?redirect=${path + searchParameter}`)
        }
        return Promise.reject(error)
    }
);

axios.interceptors.request.use((request) => {
    const token = localStorage.getItem('session_token')
    if (token) {
        // console.log('Add token to header', token);
        request.headers.Authorization = `Bearer ${token}`;
    }
    return request;
});