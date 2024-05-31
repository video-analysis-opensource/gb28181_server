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

function getDatetime(timestamp) {
  let time = new Date(timestamp);
  let year = time.getFullYear();
  const month = (time.getMonth() + 1).toString().padStart(2, '0');
  const date = (time.getDate()).toString().padStart(2, '0');
  const hours = (time.getHours()).toString().padStart(2, '0');
  const minute = (time.getMinutes()).toString().padStart(2, '0');
  const second = (time.getSeconds()).toString().padStart(2, '0');
  return year + month + date +' ' + hours + ':' + minute + ':' + second;
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




function get_item_detail_html(item_data) {
  var id = item_data['id'];
  var cam_id = item_data['cam_id'];
  var cam_name = item_data['cam_name'];
  var event_data = item_data['event_data'];
  var uptime = item_data['uptime'];
  var event_time = getDatetime(uptime*1000);
  var little_image = item_data['little_image'];
  var big_image = item_data['big_image']

  var into_counter = event_data['into_counter'];
  var out_counter = event_data['out_counter'];
  var total_counter = event_data['total_counter'];


  var inner_html = '                <img  cam_id="'+ cam_id +'" style="width: 100%" src="' + little_image + '" ' +
      '                   onclick="go_detail(this)">\n' +
      '                <div style="padding-top: 10px;text-align: center">\n' +
      '                    <div>' + cam_name + '</div> ' +
      '                    <div style="margin-bottom: 3px">更新时间： ' + event_time + '</div> ' +
      ' <p>进人数：'+ into_counter +'  出人数：'+ out_counter  +'  总人数：'+ total_counter +' </p>'+
      '                </div>\n'

    inner_html = '            <div class="col-sm-4" style="margin-top: 8px" id="' + id + '">\n' +
        inner_html +
        '            </div>'
  return inner_html
}


function init_list() {
  jQuery.post({
    url: "/people_flow_info",
    data: {
    },
    success: function (res) {
      console.log(res)
      var data = res;
      var html = '';
      Object.entries(data).forEach(function (item) {
            var item_data = item[1];
            //console.log(item)
            html += get_item_detail_html(item_data);
          }
      )

      jQuery("#main-content").html(html);
    }
  })
  return true;

}


function go_detail(ele) {
  //console.log(rtsp)
  var cam_id = jQuery(ele).attr('cam_id')
  console.log([cam_id]);
  jQuery.getJSON({
    url: "/get_people_flow_info?cam_id="+ cam_id,
    data: {"cam_id": cam_id},
    success: function (res) {
      console.log(res);
      var item_data = res;
      var id = item_data['id'];
      var cam_id = item_data['cam_id'];
      var cam_name = item_data['cam_name'];
      var event_data = item_data['event_data'];
      var uptime = item_data['uptime'];
      var event_time = getDatetime(uptime*1000);
      var little_image = item_data['little_image'];
      var big_image = item_data['big_image']

      var into_counter = event_data['into_counter'];
      var out_counter = event_data['out_counter'];
      var total_counter = event_data['total_counter'];
      var event_data_str = JSON.stringify(event_data);

      var inner_html = '                <img cam_id="'+ cam_id +'" style="height:450px;" src="' + big_image + '" ' +
          '                   id="detail-image">\n' +
          '                <div style="padding-top: 10px;text-align: center">\n' +
          '                    <div>' + cam_name + '</div> ' +
          '                    <div style="margin-bottom: 3px"  id="detail-text-info">更新时间： ' + event_time + '进人数：'+ into_counter +'  出人数：'+ out_counter  +'  总人数：'+ total_counter +'</div> ' +
          '                </div>\n' +
          '<p>原始数据：</p>'+
          '<pre style="height: 80px;white-space: pre-wrap;word-wrap: break-word;" id="detail-event-json">'+ event_data_str +'</pre>'

      var detail_dialog = dialog({
        width: 800,
        height: 660,
        title: '详情',

        content: '<div style="width: 100%;" id="detail-content">' + inner_html + '</div>'+
            '<div style="text-align: center"><a class="btn btn-info" onclick="refresh_pop_info(this)" cam_id="'+ cam_id +'">刷新</a></div>'
      });
      //detail_dialog.showModal();
      detail_dialog.showModal();
    }

  })

  //jQuery.get
  //detail_dialog.show();

}



function refresh_pop_info(ele){
  var cam_id = jQuery(ele).attr('cam_id')
  console.log([cam_id]);
  jQuery.getJSON({
    url: "/get_people_flow_info?cam_id="+ cam_id,
    data: {"cam_id": cam_id},
    success: function (res) {
      console.log(res);
      var item_data = res;
      var id = item_data['id'];
      var cam_id = item_data['cam_id'];
      var cam_name = item_data['cam_name'];
      var event_data = item_data['event_data'];
      var uptime = item_data['uptime'];
      var event_time = getDatetime(uptime*1000);
      var little_image = item_data['little_image'];
      var big_image = item_data['big_image']

      var into_counter = event_data['into_counter'];
      var out_counter = event_data['out_counter'];
      var total_counter = event_data['total_counter'];
      var event_data_str = JSON.stringify(event_data);
      jQuery("#detail-image").attr('src',big_image)
      jQuery("#detail-text-info").html('更新时间： '+ getDatetime(uptime*1000) + '进人数：'+into_counter+' 出人数：'+out_counter+' 总人数：'+total_counter);
      jQuery("#detail-event-json").html(event_data_str);
    }

  })

}

$(document).ready(function () {
      init_list()
    }
)