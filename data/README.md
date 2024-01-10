## Data Dictionary

> `beatles.csv`

|column|description|
|-|-|
|`song`|song title (**DISTINCT**). If the song is in more than one album, only one album is chosen. e.g. _Get Back_ -> in the album _Let It Be_  |
|`album`|album title that contains the song|
|`year`|recording year|
|`popularity`|popularity criteria :
||`4` : the song is in the album _Beatles 1_ (**27** songs)|
|| `3`- the song in inthe album _The Beatles 1962-1966/1967-1970_ (**27** songs)|
|| `2`- the song in inthe album _The Beatles 1962-1966/1967-1970 (2023 version)_ (**21** songs)|
|| `1`- everything else (**141** songs)|
|`duration`|duration of the song [milliseconds] (note: duration varies depending on the version)|
|`vocal`|main vocal : John, Paul, George or Ringo. Some songs have two main vocals, e.g. _She Loves You_|
|`harmony`|members who sing harmony / back chorus|
|`database_url`|link of ビートルズ楽曲データベース https://beatlesdata.info/|
|`official_youtube`|YouTube Video ID of the song|
|`spotify`|Spotify Song ID. You can open the song by https://open.spotify.com/track/<SONGID\>|
|`harmony_youtube`|YouTube Video ID of [@TheBeatlesVocalHarmony](https://www.youtube.com/@TheBeatlesVocalHarmony) |
|`bass_youtube`|YouTube Video ID of bass playing|
|`bass_tab`|link of bass TAB in https://www.songsterr.com |
|`lyrics`|lyrics of the song. line seperator `\n` is replaced with `<br>` due to csv format|

> `album.csv`

|column|description|
|-|-|
|`song`|song title (**NOT DISTINCT**)|
|`album`|album title that contains the song|
|`track`|track number in the album|

> `album_year.csv`

|column|description|
|-|-|
|`album`|album title|
|`year`|year released|