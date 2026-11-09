# Сборка Reels для @ev.belarus (бесплатно)

Ветка `media`. Видео кладём в `videos/ГГГГ-ММ-ДД_тема.mp4`.
Публичная ссылка: `https://raw.githubusercontent.com/romanpesetsky89-arch/ev-belarus-media/media/videos/<файл>.mp4`

## Стиль (утверждён владельцем)
- Обложка (сцена 1, кадр 0): яркий градиент #2bff88 → #22d3ee, сетка, жёлтая молния, огромный чёрный текст хука, тёмный бейдж с главной цифрой/вопросом. Видна с 0-й секунды.
- Остальные сцены: тёмный фон #05070d, неоновая сетка-горизонт в перспективе, частицы, сканирующий луч, стеклянные карточки с неоновой обводкой, переходы зум+блюр.
- Анимации по смыслу (батарея заряжается, полосы сравнения растут, цифры считаются, закладка «сохранить» заполняется).
- Музыка обязательна: `music.py` (свой трек, без авторских прав), акценты на сменах сцен.
- Финал: «Сохрани…» + «Подбор зарядки → @ev_car_by».
- Шрифт Inter (ExtraBold/Bold/Medium), весь текст по-русски, внутри безопасных зон (не у краёв, низ 20% — без важного текста).

## Как собрать
1. Скопировать `template_future.html` → `reel.html`, заменить сцены/тексты/массив `S` (id, начало, конец в секундах) и анимации в `render(t)` под новую тему. `window.render(t)` должна рисовать кадр для времени t.
2. `python3 tools/music.py music.wav <секунды> "<смены сцен через запятую>"`
3. `node tools/render.js reel.html frames <секунды> 25`
4. `ffmpeg -y -framerate 25 -i frames/f%05d.jpg -i music.wav -c:v libx264 -preset veryfast -crf 25 -pix_fmt yuv420p -c:a aac -b:a 128k -shortest -movflags +faststart videos/<файл>.mp4`
5. Проверить кадры (кадр 0 и середины сцен) глазами, что текст не обрезан.
6. `git add videos/<файл>.mp4 && git commit -m "..." && git push origin media`
7. Удалять ролики старше 30 дней (они уже в Metricool/Instagram).

## Голос (Стратегия 2.0, обязательно)
1. voice/<файл>.txt → push в media → Actions «tts-voiceover» создаёт voice/<файл>.mp3 (git pull через 1–2 мин).
2. `ffmpeg -y -framerate 25 -i frames/f%05d.jpg -i music.wav -i voice/<файл>.mp3 -filter_complex "[2:a]volume=1.6[v];[1:a]volume=0.18[m];[v][m]amix=inputs=2:duration=first:normalize=0[a]" -map 0:v -map "[a]" -c:v libx264 -preset veryfast -crf 25 -pix_fmt yuv420p -c:a aac -b:a 128k -t <сек> -movflags +faststart videos/<файл>.mp4`
3. Пример сцен с субтитрами под голос: work/zeekr001.html.
