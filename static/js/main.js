 function getHMS (timestamp) {
      let time = new Date(timestamp);
      let year = time.getFullYear();
      const month = (time.getMonth() + 1).toString().padStart(2, '0');
      const date = (time.getDate()).toString().padStart(2, '0');
      const hours = (time.getHours()).toString().padStart(2, '0');
      const minute = (time.getMinutes()).toString().padStart(2, '0');
      const second = (time.getSeconds()).toString().padStart(2, '0');
      return  hours + ':' + minute + ':' + second;
    }

function init_list() {
    jQuery.get({
      url:"/api/get_camera_list",
      success: function(res){
        console.log(res)
        var data=res.data;
        var html ='';
        Object.entries(data).forEach(function(item){
          var rtsp_url = item[0];
          var last_info = item[1]*1000;
          if(last_info){
                      html += '        <div class="alert alert-info" rtsp="'+rtsp_url+'">RTSP:'+ rtsp_url +'&nbsp;&nbsp;&nbsp;&nbsp;\n' +
                          '            上一帧时间： <span class="label label-info">' + getHMS(last_info) +'</span>\n' +
                          '                <button class="btn btn-warning" style="margin-left: 50px" onclick="del(this)">删除</button>\n' +
                          '                <button class="btn" onclick="go_detail(this)">查看详情</button>\n' +
                          '        </div>'

          }
          else {
            html += '<div class="alert alert-info" rtsp="'+rtsp_url+'">RTSP:' + rtsp_url + '&nbsp;&nbsp;&nbsp;&nbsp; 上一帧时间：\n' +
                '            <span class="label label-danger">无</span>\n' +
                '                <button class="btn btn-warning" style="margin-left: 50px" onclick="del(this)">删除</button>\n' +
                '                <button class="btn" onclick="go_detail(this)">查看详情</button>\n' +
                '        </div>'
          }

        })
        jQuery("#main-list").html(html)
      }
    })


}
function go_detail(ele){
  var  rtsp = $(ele).parent().attr('rtsp')
  //console.log(rtsp)
  jQuery.get({
      url:"/api/get_camera_list",
      success: function(res){
        console.log(res)
        var data=res.data;
        var has_info = false;
        Object.entries(data).forEach(function(item){
          var rtsp_url = item[0];
          var last_info = item[1]*1000;
          if(rtsp_url==rtsp && last_info>0){
            has_info=true;
          }
        })
        if(has_info){
            var image_content = '<div style="width: 100%;"><img  style="width: 100%" src="/api/real_time_image?rtsp_url='+ encodeURIComponent(rtsp) +'&time='+ (new Date()).getTime() + '"></div>';
            var detail_dialog = dialog({
              width:800,
              height:460,
            title: '摄像头详情',
              okValue:'刷新图片',
              ok:function(){
                this.content('<div style="width: 100%;"><img  style="width: 100%" src="/api/real_time_image?rtsp_url='+ encodeURIComponent(rtsp) +'&time='+ (new Date()).getTime() + '"></div>')
                return false;
              },
            content: image_content
        });
            //detail_dialog.showModal();
            detail_dialog.show();

        }
        else {
           var d = dialog({
              content: '当前摄像头暂时未捕获到流，请稍后再试'
              });
              d.show();
              setTimeout(function () {
                  d.close().remove();
              }, 1200);
        }

      }
    })

  //jQuery.get
  //detail_dialog.show();

}
function add(){
  var d = dialog({
      content: '<div class="alert alert-danger" style="display: none" id="add-err-msg"></div>' +
          '<input type="text" placeholder="请输入摄像机rtsp url" style="width: 250px" id="add-rtsp-input">',
      okValue: '提交',
      ok: function () {
        var rtsp_value =jQuery("#add-rtsp-input").val();
          jQuery.post({
            url:"/api/add_camera",
            data:{rtsp_url:rtsp_value},
            success:function(res){
              console.log(res);
              var status = res['status'];
              var message = res['message'];
              if(!status){
                jQuery("#add-err-msg").text(message)
                jQuery("#add-err-msg").show();
              }
              else {
                d.close().remove();
                init_list();

              }

            }
          })
          return false;
      },
      cancelValue: '取消',
      cancel: function () {}
  });
  d.showModal();
}


function del(ele){
  // 删除
  var  rtsp = $(ele).parent().attr('rtsp');
  var d = dialog({
      content: '确定要删除摄像机' + rtsp +'么？',
      okValue: '确定',
      ok: function () {
          jQuery.post({
            url:"/api/delete_camera",
            data:{rtsp_url:rtsp},
            success:function(res){
              console.log(res);
              init_list();
            }
          })
          return true;
      },
      cancelValue: '取消',
      cancel: function () {}
  });
  d.showModal();

 }

$(document).ready(function() {
  init_list()
}
)