import $ from 'jquery';
import React from 'react';
import AioClient from './aioclient';

export default class LoginComponent extends React.Component {
  constructor() {
    super();
    this.state = {
      loggedIn: false,
      username: '',
      pw: '',
      token: '',
      error: '',
      expires: ''
    }
  }

  handleSubmit(e) {
      e.preventDefault()
      const data = { login: this.state.username, password: this.state.pw }

      $.post(this.props.url, data).done(function(data) {
        this.setState({
          token: data.results.token,
          expires: data.results.expire_at,
          loggedIn: true,
          error: ''
        });
      }.bind(this)).fail(function(data) {
        this.setState({
          error: 'Login details not correct'
        });
      }.bind(this));
  }

  logOut() {
  }

  passInput(state, e) {
    this.setState({
      [state]: e.target.value
    });
  }

  render() {
    return (
      <div>
        <h1>React Login</h1>
        { this.state.loggedIn ? <LoginDetails server={this.props.server} token={this.state.token} user={this.state.username} expires={this.state.expires} logout={this.logOut.bind(this)}/> : <Form change={this.passInput.bind(this)} submit={this.handleSubmit.bind(this)} user={this.state.username} pw={this.state.pw} error={this.state.error} /> }
      </div>
    )
  }
}

class LoginDetails extends React.Component {
  render() {
    return(
      <div>
        <p><span>Username:</span> {this.props.user}</p>
        <p><span>Token:</span> {this.props.token}</p>
        <p><span>Expires at:</span> {this.props.expires}</p>
        <button onClick={this.props.logout}>Logout</button>
        <AioClient server={this.props.server}>
      </div>
    )
  }
}

class Form extends React.Component {

  render() {
    return(
      <form onSubmit={this.props.submit}>
        <Username user={this.props.user} change={this.props.change}/>
        <Password pw={this.props.pw} change={this.props.change}/>
        <Submit submit={this.props.submit}/>
        <p id="error">{this.props.error}</p>
      </form>
    )
  }
}

class Username extends React.Component {
  render() {
    return(
      <input placeholder="Username" type="text" value={this.props.user} onChange={(e) => this.props.change('username', e)} />
    )
  }
}

class Password extends React.Component {
  render() {
    return(
      <input placeholder="Password" type="password" value={this.props.user} onChange={(e) => this.props.change('pw', e)} />
    )
  }
}

class Submit extends React.Component {
  render() {
    return(
      <button type="submit" onClick={this.props.submit}>Login</button>
    )
  }
}
