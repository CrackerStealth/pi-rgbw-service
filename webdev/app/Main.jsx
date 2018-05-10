import React from 'react';
import ReactDOM from 'react-dom';

import darkBaseTheme from 'material-ui/styles/baseThemes/darkBaseTheme';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';

import AppBar from 'material-ui/AppBar';
import Paper from 'material-ui/Paper';
import Avatar from 'material-ui/Avatar';
import {Card, CardActions, CardHeader, CardText} from 'material-ui/Card';
import Subheader from 'material-ui/Subheader'
import Slider from 'material-ui/Slider';
import FlatButton from 'material-ui/FlatButton';

import IconOff from 'material-ui/svg-icons/device/brightness-low';
import IconOn from 'material-ui/svg-icons/device/brightness-high';

class App extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {date: null, hostname: null, lights: []};
  }
  
  componentDidMount() {
      fetch('/api/')
        .then(result=>result.json())
        .then(items=>this.setState({date: items.date, hostname: items.hostname, lights: items.lights}))
  }

  render() {
    return (
      <MuiThemeProvider muiTheme={getMuiTheme(darkBaseTheme)}>
        <div>
          <AppBar showMenuIconButton={false} title="Light Controller" titleStyle={{fontWeight: 'bold', textAlign: 'center', color: '#FFFFFF'}}/>
          {
            this.state.lights.map(e => (
              <RgbwLight key={e} name={e} />
            ))
          }
        </div>
      </MuiThemeProvider>
    );
  }
}

class RgbwLight extends React.Component {
  constructor(props) {
    super(props);
    
    this.state = {onoff_state: false,
                  red_state: 0, green_state: 0, blue_state: 0,
                  warm_white_state: 0, cool_white_state: 0,
                  enable_rgb: false, enable_ww: false, enable_cw: false,
                  card_open: false};
    
    this.handleExpandChange = this.handleExpandChange.bind(this);
    this.handleToggleOn = this.handleToggleOn.bind(this);
    this.handleToggleOff = this.handleToggleOff.bind(this);
    this.handleRedColorChange = this.handleRedColorChange.bind(this);
    this.handleGreenColorChange = this.handleGreenColorChange.bind(this);
    this.handleBlueColorChange = this.handleBlueColorChange.bind(this);
    this.handleWarmWhiteColorChange = this.handleWarmWhiteColorChange.bind(this);
    this.handleCoolWhiteColorChange = this.handleCoolWhiteColorChange.bind(this);
    this.handleColorChange = this.handleColorChange.bind(this);
  }
  
  queryRestApi() {
    fetch('/api/' + this.props.name + '/')
        .then(result=>result.json())
        .then(items=>this.setState({onoff_state: items.onoff_state,
                                    red_state: items.red_state, green_state: items.green_state, blue_state: items.blue_state,
                                    warm_white_state: items.warm_white_state, cool_white_state: items.cool_white_state,
                                    enable_rgb: items.enable_rgb, enable_ww: items.enable_ww, enable_cw: items.enable_cw,
                                    card_open: (items.onoff_state == false ? false : this.state.card_open)}))
  
  }
  
  componentWillMount() {
    this.queryRestApi()
  }
  
  handleExpandChange(expanded) {
    this.setState({card_open: expanded});
  };
  
  handleToggleOn(event) {
    var _this = this
    var response = {
      onoff_state: true,
    };
    
    fetch('/api/' + this.props.name + '/',
        {
           method: "POST",
           body: JSON.stringify(response)
        })
      .then(function(res){ return res.json(); })
      .then(function(data){ _this.queryRestApi() })
  }
  
  handleToggleOff(event) {
    var _this = this
    var response = {
      onoff_state: false,
    };
    
    fetch('/api/' + this.props.name + '/',
        {
           method: "POST",
           body: JSON.stringify(response)
        })
      .then(function(res){ return res.json(); })
      .then(function(data){ _this.queryRestApi() })
  }
  
  handleRedColorChange(event, value) {
    this.handleColorChange(event, value, this.state.green_state, this.state.blue_state, null, null)
  }
  
  handleGreenColorChange(event, value) {
    this.handleColorChange(event, this.state.red_state, value, this.state.blue_state, null, null)
  }
  
  handleBlueColorChange(event, value) {
    this.handleColorChange(event, this.state.red_state, this.state.green_state, value, null, null)
  }
  
  handleWarmWhiteColorChange(event, value) {
    this.handleColorChange(event, null, null, null, value, null)
  }
  
  handleCoolWhiteColorChange(event, value) {
    this.handleColorChange(event, null, null, null, null, value)
  }
  
  handleColorChange(event, red, green, blue, warm_white, cool_white) {
    var _this = this
    var response = {}
    
    if (warm_white != null) {
      response['warm_white_state'] = warm_white
    }
    if (cool_white != null) {
      response['cool_white_state'] = cool_white
    }
    if (red != null && green != null && blue != null) {
      response['red_state'] = red
      response['green_state'] = green
      response['blue_state'] = blue
    }
    
    fetch('/api/' + this.props.name + '/',
        {
           method: "POST",
           body: JSON.stringify(response)
        })
      .then(function(res){ return res.json(); })
      .then(function(data){ _this.queryRestApi() })
  }
  
  getAltText() {
    var text = 'Supports: '
    
    if (this.state.enable_rgb) text += 'RGB, '
    if (this.state.enable_ww) text += 'Warm White, '
    if (this.state.enable_cw) text += 'Cool White, '
    
    text = text.substring(0, text.length-2)
    
    return text
  }
  
  getRgbColor() {
    if (this.state === null) return "#000000";
    
    var red = this.state.red_state.toString(16);
    var green = this.state.green_state.toString(16);
    var blue = this.state.blue_state.toString(16);
    
    if (red.length == 1) red = '0' + red;
    if (green.length == 1) green = '0' + green;
    if (blue.length == 1) blue = '0' + blue;
    
    return ("#" + red + green + blue);
  }
  
  getStateColor() {
    if (this.state === null) return "#000000";
    
    if (this.state.enable_ww && this.state.warm_white_value > 0) return "#FFAC44";
    if (this.state.enable_cw && this.state.cool_white_value > 0) return "#FFFFFF";
    
    return this.getRgbColor();
  }
  
  getStateIcon() {
    var color = this.getStateColor();
    
    if (this.state.onoff_state){
      return (
        <Avatar icon={<IconOn />} color={color} />
      );
    } else {
      return (
        <Avatar icon={<IconOff />} />
      );
    }
  }
      
  render() {
    var textSupports = this.getAltText();
    var stateIcon = this.getStateIcon();
    var rgb = this.getRgbColor();
    
    return (
      <Card style={{margin: 15}} expanded={this.state.card_open} onExpandChange={this.handleExpandChange}>
        <CardHeader title={this.props.name} subtitle={textSupports} avatar={stateIcon} actAsExpander={true} showExpandableButton={this.state.onoff_state} />
        <CardText expandable={true}>
          { this.state.enable_rgb &&
          <div>
            <Subheader>RGB</Subheader>
            <div style={{width: '100%', height: 40, backgroundColor: rgb}} />
            <Slider min={0} max={255} step={1} value={this.state.red_state} onChange={this.handleRedColorChange} />
            <Slider min={0} max={255} step={1} value={this.state.green_state} onChange={this.handleGreenColorChange} />
            <Slider min={0} max={255} step={1} value={this.state.blue_state} onChange={this.handleBlueColorChange} />
          </div>
          }
          { this.state.enable_ww &&
          <div>
            <Subheader>Warm White</Subheader>
            <Slider min={0} max={255} step={1} value={this.state.warm_white_state} onChange={this.handleWarmWhiteColorChange} />
          </div>
          }
          { this.state.enable_wcw &&
          <div>
            <Subheader>Cool White</Subheader>
            <Slider min={0} max={255} step={1} value={this.state.cool_white_state} onChange={this.handleCoolWhiteColorChange} />
          </div>
          }
        </CardText>
        <CardActions>
          <FlatButton label="Turn On" disabled={this.state.onoff_state} onClick={this.handleToggleOn} />
          <FlatButton label="Turn Off" disabled={!this.state.onoff_state} onClick={this.handleToggleOff}/>
        </CardActions>
      </Card>
    );
  }
}

ReactDOM.render(<App />, document.getElementById('app'));
