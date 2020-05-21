# CoronaNotify

> 뉴스보다 빠른 코로나19 현황 Push 알림 프로젝트  

**코로나19 현황 정보 제공 사이트**에서 코로나19 현황 업데이트를 정기적으로 체크하고, Line Bot을 통해 Push 해주는 소스코드

## 정보 수집 사이트 목록  

### PIPELINES.py

*  class Pipeline

| Pipeline | Role | Organization | Request URL | Note |
| :------: | :------: | :------: | :------: | :------: |
| 1 | 국내 0시 기준 현황 정보 수집 | 중앙재난안전대책본부 | [바로가기](http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun=) |
| 2 | 국내 0시 기준 현황 정보 수집 | 질병관리본부 | [바로가기](https://www.cdc.go.kr/board/board.es?mid=a20501000000&bid=0015) | 
| 3 | 국내 0시 기준 현황 정보 수집 | 중앙재난안전대책본부 | [바로가기](http://ncov.mohw.go.kr/tcmBoardList.do?brdId=&brdGubun=&dataGubun=&ncvContSeq=&contSeq=&board_id=140&gubun=) |
| ~~[-4-]~~ | ~~[-국외 현황 정보 수집-]~~ | ~~[-중앙재난안전대책본부-]~~ | [~~[-바로가기-]~~](http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun=) | 발표 종료 |
| ~~[-5-]~~ | ~~[-국내 16시 기준 현황 정보 수집-]~~ | ~~[-중앙재난안전대책본부-]~~ | [~~[-바로가기-]~~](http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=&brdGubun=&ncvContSeq=&contSeq=&board_id=&gubun=) | 발표 종료 |
| 6 | 국내 0시 기준 현황 정보 수집 | 보건복지부 | [바로가기](http://www.mohw.go.kr/react/al/sal0301ls.jsp?PAR_MENU_ID=04&MENU_ID=0403) |
| 7 | 국내 0시 기준 현황 정보 수집 | 중앙재난안전대책본부 | [바로가기](http://ncov.mohw.go.kr/) |

### FetchBot2.py

*  class FetchBot

| Name | Role | Organization | Request URL | Note |
| :------: | :------: | :------: | :------: | :------ |
| get_world_data | 국외 현황 정보 수집 | Johns Hopkins Univ. | [바로가기](https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=200&cacheHint=true)

### LocalFetchBot.py

*  class MGLocalFetchBot

| Name | Role | Organization | Request URL | Note |
| :------: | :------: | :------: | :------: | :------ |
| Fetch_local_case1 | 수원시 현황 정보 수집 | 수원시청 | [바로가기](https://www.cdc.go.kr/board/board.es?mid=a20501000000&bid=0015) | 
|  | 용인시 현황 정보 수집 | 용인시청 | [바로가기](http://www.yongin.go.kr/index.do) | 
|  | 성남시 현황 정보 수집 | 성남시청 | [바로가기](http://www.seongnam.go.kr/coronaIndex.html) |
| Fetch_local_case2 | 천안시 현황 정보 수집 | 천안시청 | [바로가기](http://27.101.50.5/prog/stat/corona/json.do) |

## How to use

*  APIKey.py
```python
API_KEY_FOR_NOTI = 'Line Notify Token for Notification' #Optional
API_KEY_FOR_ERROR = 'Line Notify Token for Error Message' #Required

API_KEY_FOR_BOT = 'Line Bot Token for Notification' #Required
API_REQUEST_URL = 'https://api.line.me/v2/bot/message/push' #Required

GROUP_ID = 'Group ID' #Required
TEST_GROUP_ID = 'Test Group ID' #Optional
```
*  FetchBot.sh

```
cd /PATH
python3 FetchBot2.py
```


*  Crontab -e

```
57 9 * * * /PATH/FetchBot.sh
```

## Preview
<img src="/docs/v4.jpg" width="30%">