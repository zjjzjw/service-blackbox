### DB: black_box
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Table_name</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>pages</td>
      <td>页面信息</td>
   </tr>
   <tr>
      <td>page_time</td>
      <td>页面执行时间</td>
   </tr>
   <tr>
      <td>slow_requests</td>
      <td>慢查询</td>
   </tr>
   <tr>
      <td>slow_requests_analysis</td>
      <td>慢查询分析</td>
   </tr>
   <tr>
      <td>everyday_analysis</td>
      <td>每天数据分析表</td>
   </tr>
   <tr>
      <td>sql_query_count</td>
      <td>sql查询数</td>
   </tr>
</table>

### TABLE: pages
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>page_id（主键）</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_name</td>
      <td>VARCHAR（50）</td>
      <td>页面名称</td>
   </tr>
   <tr>
      <td>controller_name</td>
      <td>VARCHAR（50）</td>
      <td>控制器名称</td>
   </tr>
   <tr>
      <td>status</td>
      <td>INT</td>
      <td>0或1</td>
   </tr>
   <tr>
      <td>target</td>
      <td>INT</td>
      <td>阈值</td>
   </tr>
</table>
注：为controller_name添加索引controller_name_index

### TABLE: page_time
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>id（主键）</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_id</td>
      <td>INT</td>
      <td>与page表page_id对应</td>
   </tr>
   <tr>
      <td>app_time</td>
      <td>VARCHAR（255）</td>
      <td>App名称</td>
   </tr>
   <tr>
      <td>module_time</td>
      <td>VARCHAR（255）</td>
      <td>模块时间</td>
   </tr>
   <tr>
      <td>frame_time</td>
      <td>VARCHAR（255）</td>
      <td>框架时间</td>
   </tr>
   <tr>
      <td>execution_time</td>
      <td>VARCHAR（255）</td>
      <td>执行时间</td>
   </tr>
   <tr>
      <td>created</td>
      <td>DATETIME</td>
      <td>数据插入时间</td>
   </tr>
   <tr>
      <td>date</td>
      <td>INT</td>
      <td>日期</td>
   </tr>
</table>
注：为page_id和created添加联合索引pageId_created_index;为page_id和date添加联合索引pageId_date_index

### TABLE: slow_requests
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>id</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_id</td>
      <td>INT</td>
      <td>与page表page_id对应</td>
   </tr>
   <tr>
      <td>app_name</td>
      <td>VARCHAR（50）</td>
      <td>App名称</td>
   </tr>
   <tr>
      <td>url</td>
      <td>VARCHAR（255）</td>
      <td>链接地址</td>
   </tr>
   <tr>
      <td>content</td>
      <td>TEXT</td>
      <td>内容</td>
   </tr>
   <tr>
      <td>execution_time</td>
      <td>INT</td>
      <td>时间</td>
   </tr>
   <tr>
      <td>minute</td>
      <td>VARCHAR（12）</td>
      <td>分钟</td>
   </tr>
   <tr>
      <td>created</td>
      <td>DATETIME</td>
      <td>数据插入时间</td>
   </tr>
</table>
注：为execution_time添加索引execution_time_index;为page_id和minute添加联合索引pageId_minute_index

### TABLE: slow_requests_analysis
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>id</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_id</td>
      <td>INT</td>
      <td>与page表page_id对应</td>
   </tr>
   <tr>
      <td>content</td>
      <td>TEXT</td>
      <td>内容</td>
   </tr>
   <tr>
      <td>created</td>
      <td>DATETIME</td>
      <td>数据插入时间</td>
   </tr>
</table>
注：为page_id和created添加联合索引pageId_created_index

### TABLE: everyday_analysis
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>id（主键）</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_id</td>
      <td>INT</td>
      <td>与page表page_id对应</td>
   </tr>
   <tr>
      <td>app_time</td>
      <td>VARCHAR（255）</td>
      <td>App名称</td>
   </tr>
   <tr>
      <td>module_time</td>
      <td>VARCHAR（255）</td>
      <td>模块时间</td>
   </tr>
   <tr>
      <td>frame_time</td>
      <td>VARCHAR（255）</td>
      <td>框架时间</td>
   </tr>
   <tr>
      <td>execution_time</td>
      <td>VARCHAR（255）</td>
      <td>执行时间</td>
   </tr>
   <tr>
      <td>content</td>
      <td>TEXT</td>
      <td>各断点时间</td>
   </tr>
   <tr>
      <td>slow_requests</td>
      <td>VARCHAR(1000)</td>
      <td>慢请求</td>
   </tr>
   <tr>
      <td>date</td>
      <td>INT</td>
      <td>日期</td>
   </tr>
</table>
注：为page_id和date添加联合索引pageId_date_index

### TABLE: sql_count
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>id</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_id</td>
      <td>INT</td>
      <td>与page表page_id对应</td>
   </tr>
   <tr>
      <td>count</td>
      <td>INT</td>
      <td>每分钟sql查询数</td>
   </tr>
   <tr>
      <td>minute</td>
      <td>VARCHAR（12）</td>
      <td>分钟</td>
   </tr>
</table>
注：为page_id和minute添加联合索引pageId_minute_index

### TABLE: sql_everyday_analysis
<table class="table table-condensed">
   <tr style="color:white; background:#808080;">
      <td>Name</td>
      <td>Data_type</td>
      <td>Description</td>
   </tr>
   <tr>
      <td>id</td>
      <td>INT</td>
      <td>自增量</td>
   </tr>
   <tr>
      <td>page_id</td>
      <td>INT</td>
      <td>与page表page_id对应</td>
   </tr>
   <tr>
      <td>count</td>
      <td>INT</td>
      <td>每天总数</td>
   </tr>
   <tr>
      <td>date</td>
      <td>INT</td>
      <td>日期</td>
   </tr>
</table>
注：为page_id和date添加联合索引pageId_date_index
