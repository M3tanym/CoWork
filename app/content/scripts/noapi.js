// function func(f) {
//   // TODO decorator??
//   console.log("decorator");
//   return f;
// }

function uuidv4() {
  return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
    (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
  );
}

class NoAPI {
  constructor(host) {
    this.host = host;
    this.ws = null;
    this.py_calls = {};
    this.js_calls = {};

    this.onmessage = (_) => {};
    this._connectWS();
  }

  _connectWS() {
    console.log("Connecting");
    this.ws = new WebSocket(this.host);
    this.ws.onopen = (_) => {console.log("Connected");};
    this.ws.onmessage = (e) => {this._process_msg(e);};

    this.ws.onclose = (_) => {
      console.log("Closed");
      setTimeout(() => {
        this._connectWS();
      }, 1000);
      // TODO backoff
    };

    this.ws.onerror = (_) => {
      console.error("Error");
      this.ws.close();
    };
  }

  _process_msg(e) {
    let data = JSON.parse(e.data);
    // console.log('Message', data);
    let t = data['type'];
    let behaviors = {
      'info': (data) => {this._handle_info(data)},
      'call': (data) => {this._handle_call(data)},
      'return': (data) => {this._handle_return(data)}
    };
    if (t in behaviors) {
      behaviors[t](data);
    }
    else {
      console.log('Unknown message', data);
    }
  }

  _handle_info(data) {
    this.onmessage(data['data']);
  }

  _handle_call(data) {
    // console.log('CALL HANDLER');
    console.log("CALL", data);
    let fn = data['fn'];
    let fid = data['fid'];
    let args = data['args'];
    let p = new Promise((resolve, reject) => {
      let ret = this.js_calls[fn](args);
      resolve(ret);
    });
    p.then((ret) => {
      this.raw({'type': 'return', 'fid': fid, 'ret': ret});
    });
  }

  _handle_return(data) {
    // console.log('RETURN HANDLER');
    let fn = data['fn'];
    let fid = data['fid'];
    let ret = data['ret'];
    this.py_calls[fid].resolve(ret);
  }

  _return_waiter(fn, fid) {
    // console.log('RETURN WAITER');
    return;
  }

  register(fn, f) {
    this.js_calls[fn] = f;
  }

  raw(json_msg) {
    this.ws.send(JSON.stringify(json_msg));
  }

  info(msg='') {
    this.raw({'type': 'info', 'msg': msg});
  }

  call(fn) {
    let args, kwargs;
    if (arguments.length > 1) {
      args = arguments[1];
      if (args.constructor !== Array) {
        args = [args];
      }
    }
    if (arguments.length > 2) {
      kwargs = arguments[2];
    }

    // let fid = crypto.randomUUID();
    let fid = uuidv4();
    this.raw({'type': 'call', 'fn': fn, 'fid': fid, 'args': args, 'kwargs': kwargs});
    return new Promise((resolve, reject) => {
      this.py_calls[fid] = {'resolve': resolve, 'reject': reject};
    });
  }
}
