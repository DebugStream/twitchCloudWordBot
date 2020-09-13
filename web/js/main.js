// Create a client instance
var client = new Paho.MQTT.Client("localhost", 8000, "clientId");

// QUEUE
function PriorityQueue(){
  
  this.dataStore = Array.prototype.slice.call(arguments, 0);
  this.enqueue = enqueue; 
  this.dequeue = dequeue;
  this.isEmpty = isEmpty;
  this.print = print;
  
  function enqueue (element) {
    this.dataStore.push(element);
  }
  
  function dequeue(){
    var priority = this.dataStore[0].priority;
    var priorizedItem = 0;
    this.dataStore.forEach(function (item, index ){
      if(item.priority < priority) {
        priority = item.priority;
        priorizedItem = index;
      }
    });
    return this.dataStore.splice(priorizedItem, 1)[0];
  }
  
  function isEmpty(){
    return this.dataStore.length == 0;  
  }
  
  function print(){
    return this.dataStore.map(function(row){
      return { terms: row.terms, author: row.author }
    });
  }
}

var QUEUE = new PriorityQueue()

OPTIONS = {
  list: [],
  fontFamily: 'Ranchers, cursive, sans-serif',
  color: 'random-light',
  shape: 'squared',
  gridSize: Math.round(16 * $('#canvas').width() / 1024),
  weightFactor: function (size) {
    switch (true) {
      case size == 1:
        return size*20
        break;
      case size < 5:
        return size*25
        break;
      case size < 20:
        return size*15
        break;
      case size > 80:
          return size*3
          break;          
      default:
        return size
        break;
    }
  },
  backgroundColor: 'rgb(0,0,0)'
}

// set callback handlers
client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;

// connect the client
client.connect({onSuccess:onConnect});

// called when the client connects
function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("onConnect");
  client.subscribe("cloudwords");
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    alert(responseObject.errorMessage);
  }
}

function renderCloudWord(message) {
  OPTIONS.list = message.response;
  WordCloud(document.getElementById('word_cloud'), OPTIONS);
}

// called when a message arrives
function onMessageArrived(message) {
  message = JSON.parse(message.payloadString);
  console.log(message);
  QUEUE.enqueue(message);
  renderQueue()
};

function renderQueue() {
  if(QUEUE.isEmpty()) { 
    
    return; }
  var _queue = QUEUE.print()
  html = ejs.render(`
    <ol>
      <% for(var i = 0; i < list.length; ++i) {%>
        <li class="<%=i === 0 ? "current_term": "" %>"><%=i === 0 ? "👀": "" %> @<%=list[i].author%>: <%=list[i].terms%></li>
      <% } %>
    </ol>
  `, 
  {list: _queue});
  $('.queue_list').html(html);
}


var timeleft = 20;
var downloadTimer = setInterval(function(){
  if(timeleft <= 0){
    timeleft = 20
    document.getElementById("countdown").innerHTML = "⏰ " + timeleft + "s";

    if (!QUEUE.isEmpty()) {
      renderQueue()
      var elements = QUEUE.dequeue();
      renderCloudWord(elements)
    }    

  } else {
    document.getElementById("countdown").innerHTML = "⏰ " + timeleft + "s";
  }
  timeleft -= 1;
}, 1000);