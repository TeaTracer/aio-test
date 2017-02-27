import React from 'react';
import ReactDOM from 'react-dom';
import AioClient from './components/aioclient';


window.onload = () => {
    ReactDOM.render(
        <AioClient server="wss://127.0.0.1:1236/socket/" />,
        document.getElementById("aio")
    );
};
