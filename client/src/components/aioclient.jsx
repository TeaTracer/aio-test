import React from 'react';

export default class AioClient extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            data: undefined,
            is_error: false
        };
    }

    componentDidMount() {
        var ws = new WebSocket(this.props.server + this.props.token);

        ws.onmessage = (event) => {
            var data = JSON.parse(event.data);
            this.setState({"data": data});
            console.log(data);
        };

        var sendRequest = () => {
            var request = {
                method: "echo",
                params: []
            };
            ws.send(JSON.stringify(request))
        }

        ws.onopen = () => {
            setInterval( _ => sendRequest(), 2000);
        }
        ws.onerror = (e) => {
            this.setState({'is_error': true});
            console.log('Error');
        }
      }

    render() {
        return (
            <div>
                <div> Test!!! </div>
                <div> {!this.state.is_error ? 'OK!' : 'ERROR!'} </div>
            </div>
        );
    }

};
