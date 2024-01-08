# LINE Messaging API + Flask

an information retrieval tool for **The Beatles songs**

Explanation of code in Japanese : see [Qiita](https://qiita.com/nozomiyamada/items/f6c6816e02359e08a74e)

- `Python==3.11.6`
- `pip==23.3.1`
- `Flask==3.0.0`
- `line-bot-sdk==3.7.0` use v3

LINE BOT ID : `@711mvjit`
https://line.me/R/ti/p/%40711mvjit


![img](img/711mvjit.png)

## Features

**send `How To Use` to show how to use**

1. **Official YouTube Mode**
    Find official YouTube video. Send only a song title.
    e.g. `Hey Jude`

2. **Lyrics Mode**
    Show lyrics of a song. Send a song title with the command `lyrics/歌詞`.
    e.g. `lyrics Help`

3. **Harmony Mode**
    Find a video of “The Beatles Vocal Harmony”. Send a song title with the command `harmony/chorus/コーラス`
    e.g. `chorus nowhere man`

4. **Bass TAB Mode**
    Find Bass TAB from songsterr.com. Send a song title with the command `basstab`
    e.g. `basstab boys`

5. **Bass Video Mode**
    Find a YouTube video of bass play. Send a song title with the command `bass`
    e.g. `bass 909`

6. **Random Mode**
    Pick one song at random. Send the command `random`

7. **Info Mode**
    Show link of https://beatlesdata.info. Send a song title with the command `info`
    e.g. `info get back`

8. **Quiz Mode**
    Quiz to guess the song title from the part of the lyrics. Send the command `quiz`




