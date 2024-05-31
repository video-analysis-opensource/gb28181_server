
var image_domain = window.location.href.indexOf('172.99') > -1? 'http://172.99.128.18:8888/': 'http://10.4.14.66:8888/'

function getHMS(timestamp) {
  let time = new Date(timestamp);
  let year = time.getFullYear();
  const month = (time.getMonth() + 1).toString().padStart(2, '0');
  const date = (time.getDate()).toString().padStart(2, '0');
  const hours = (time.getHours()).toString().padStart(2, '0');
  const minute = (time.getMinutes()).toString().padStart(2, '0');
  const second = (time.getSeconds()).toString().padStart(2, '0');
  return hours + ':' + minute + ':' + second;
}

function show_msg(content) {
  var d = dialog({
    content: content
  });
  d.show();
  setTimeout(function () {
    d.close().remove();
  }, 1200);

}


$("#submitBtn").click(function(){

  var targetUrl = $("#reportForm").attr("action");
  var data = $("#reportForm").serialize();
   $.ajax({
    type:'post',
    url:targetUrl,
    cache: false,
    data:data,  //重点必须为一个变量如：data
    dataType:'json',
    success:function(data){
      show_msg('success');
      window.location.reload();
    },
    error:function(){
     alert("请求失败")
    }
   })

})



function verify(id, status) {
  jQuery.post({
    url: "/get_event_item",
    data: {"id": id},
    success: function (res) {
      var image_url = res['event_data']['picpath'] || '';
      var cam_name = res['cam_name'];
      var event_data = res['event_data'];
      var event_time = event_data['time'];
      //console.log(res);
      console.log(image_url)
      var detail_dialog = dialog({
        width: 700,
        height: 560,
        title: status == 1 ? '确定要上报事件么？' : '确定要标记为程序误判么',
        okValue: status == 1 ? '上报' : '标记误判',
        content: '<div style="width: 100%;">' +
            '<p>' + cam_name + '</p>' +
            '<p>' + event_time + '</p>' +
            '<img  style="width: 100%" src="' +  image_domain + image_url + '"></div>',

        ok: function () {
          jQuery.post({
            url: "/verify_event",
            data: {id: id, verify_status: status},
            success: function (res) {
              var msg = res['message'];
              var _status = res['status'];
              var data = res['data'];
              if (!_status) {
                show_msg(msg)
              } else {
                show_msg(msg);

              }
              refresh_item(id);
            }
          })
          return true;
        },
        cancelValue: '取消',
        cancel: function () {
        }
      });
      detail_dialog.showModal();

    }
  })
}

function refresh_item(id) {
  jQuery.post({
    url: "/get_event_item",
    data: {"id": id},
    success: function (res) {
      var item_data = res;
      var html_info = get_item_detail_html(item_data,false);
      jQuery("#"+id).html(html_info)
      //console.log(res);

    }
  })
}
