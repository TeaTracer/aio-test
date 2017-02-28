import React from 'react';
import ReactDOM from 'react-dom';
import LoginComponent from './components/login';


window.onload = () => {
    ReactDOM.render(
        <LoginComponent url="https://127.0.0.1:8080/login" server="wss://127.0.0.1:1236/api/remote" />,
        document.getElementById("aio")
    );
};
