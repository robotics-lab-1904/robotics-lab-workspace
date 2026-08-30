# OV5647 на Orange Pi Zero 3W с ядром Allwinner `sunxi-vin`

## Полный отчёт, инструкция по сборке, установке, диагностике и дальнейшему изучению

Дата фиксации рабочего состояния: 12 августа 2026 года.

Проверенная конфигурация:

- плата: Orange Pi Zero 3W на Allwinner A733 (`sun60iw2`);
- ОС: Armbian/Ubuntu Noble;
- ядро: `6.6.98-vendor-sun60iw2`;
- камера: OmniVision OV5647, 5 Мп;
- интерфейс: MIPI CSI-2, две линии данных;
- активен второй CSI-тракт платы;
- устройство захвата: `/dev/video8`;
- медиаустройство: `/dev/media0`;
- адрес OV5647: `0x36` в 7-битной форме I²C или `0x6c` в 8-битной форме Allwinner CCI;
- поддерживаемые режимы драйвера: 1280×720@30, 1920×1080@30 и 2592×1944@15;
- формат сенсора: 10-битный Bayer BGGR (`MEDIA_BUS_FMT_SBGGR10_1X10`, V4L2 FourCC `BG10`).

Рабочие файлы проекта находятся в каталоге:

```text
/home/artm1904/Program/Robot/os/camera-ov5647
```

Исходный код адаптированного драйвера находится здесь:

```text
/home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2/
  bsp/drivers/vin/modules/sensor/ov5647.c
```

> **Важно:** этот документ описывает именно vendor-ядро Orange Pi/Allwinner.
> Инструкции для Raspberry Pi, mainline Linux и обычного `libcamera` нельзя
> механически переносить на данную систему.

---

## 1. Что представляет собой камерный тракт

Камера — это не просто `/dev/videoN`. На этой платформе изображение проходит
через несколько аппаратных и программных узлов:

```text
OV5647
  │  RAW10, MIPI CSI-2, 2 lanes
  ▼
sunxi_mipi.1
  ▼
sunxi_csi.1
  ▼
sunxi_tdm_rx.0
  ▼
sunxi_isp.0
  ▼
sunxi_scaler.8
  ▼
vin_cap.8
  ▼
/dev/video8
```

Роли компонентов:

- **OV5647** формирует необработанный Bayer RAW10;
- **MIPI CSI-2 receiver** принимает последовательный поток с камеры;
- **CSI/TDM** маршрутизирует поток внутри SoC;
- **ISP** выполняет дебайеризацию, экспозицию, баланс белого и цветовую обработку;
- **scaler** меняет размер/выходной формат;
- **VIN capture** выдаёт кадры приложению через V4L2.

Топологию можно увидеть командой:

```bash
media-ctl -p -d /dev/media0
```

---

## 2. Почему штатный драйвер OV5647 не подошёл напрямую

В исходном дереве Linux уже есть mainline-драйвер:

```text
drivers/media/i2c/ov5647.c
```

Но используемый образ построен вокруг vendor-стека Allwinner:

```text
bsp/drivers/vin/
```

Этот стек использует собственные интерфейсы:

- CCI вместо обычного прямого I²C-взаимодействия mainline-драйвера;
- `sensor_helper`;
- `vin_io`;
- специальные `VIDIOC_VIN_*` ioctl;
- собственную модель питания, тактирования и GPIO;
- собственную регистрацию двух экземпляров сенсора;
- собственное описание камер в DTB (`sensor0_mname`, `sensor2_mname` и т. п.).

Поэтому было недостаточно включить стандартный `CONFIG_VIDEO_OV5647`. Нужен был
драйвер, совместимый с API `sunxi-vin` именно этой ветки ядра.

---

## 3. Первичная диагностика платы

### 3.1. Подключение по SSH

Использовалось подключение:

```bash
ssh root@192.168.1.236
```

Пароль намеренно не записан в этот документ. Для постоянной работы лучше
настроить SSH-ключи.

### 3.2. Проверка версии ядра и архитектуры

```bash
uname -a
uname -r
uname -m
```

Критический результат:

```text
6.6.98-vendor-sun60iw2
aarch64
```

Модуль ядра обязан собираться для **точно такой же** строки `uname -r`.

### 3.3. Проверка заголовков ядра

```bash
readlink -f /lib/modules/$(uname -r)/build
ls -la /usr/src/linux-headers-$(uname -r)
```

На плате заголовки находились здесь:

```text
/usr/src/linux-headers-6.6.98-vendor-sun60iw2
```

### 3.4. Проверка конфигурации и module ABI

```bash
grep -E 'CONFIG_MODULES=|CONFIG_MODVERSIONS=' \
  /lib/modules/$(uname -r)/build/.config
```

В проверенном ядре `CONFIG_MODVERSIONS` не был включён. Это упрощает сборку
внешнего модуля, но совпадение `vermagic` всё равно обязательно.

### 3.5. Сохранение исходного DTB

До любых изменений был сделан бэкап:

```bash
DTB_DIR=/boot/dtb-$(uname -r)/allwinner

cp -a \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.dtb" \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.pre-ov5647-20260811.dtb"

sha256sum \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.pre-ov5647-20260811.dtb"
```

Контрольная сумма исходного DTB:

```text
1eb1160f92dd1d566af920002583c67fbbb6eb35d190a62fb8f0bc1236bb74e1
```

---

## 4. Получение исходников ядра

Использовался официальный репозиторий Orange Pi:

```bash
git clone \
  --filter=blob:none \
  --branch orange-pi-6.6-sun60iw2 \
  https://github.com/orangepi-xunlong/linux-orangepi.git \
  linux-orangepi-sun60iw2

cd linux-orangepi-sun60iw2
git rev-parse HEAD
```

Проверенная ревизия:

```text
8a9be72c9006a87f786736b3aa4e2dfd971c1429
```

Ветка:

```text
orange-pi-6.6-sun60iw2
```

Также использовался Armbian Build Framework:

```bash
git clone https://github.com/armbian/build.git build
```

В нём семейство платы описано в:

```text
build/config/sources/families/sun60iw2.conf
build/config/boards/orangepizero3w.csc
```

---

## 5. Как был разработан драйвер `ov5647.ko`

### 5.1. Основа адаптации

Для правильного API ядра 6.6 за основу структуры был взят существующий vendor-
драйвер:

```text
bsp/drivers/vin/modules/sensor/ov5648_mipi.c
```

Таблицы регистров и часть логики OV5647 были взяты из опубликованного прямо в
сообщениях Allwinner Developer Forum драйвера для V851S/Tina Linux:

<https://bbs.aw-ol.com/topic/4638/v851s-tina-linux-ov5647-%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8F%E6%B2%A1%E6%9C%89-dmesg>

Это не вложение темы Orange Pi. Предыдущая рабочая заметка ошибочно связывала
исходник с обсуждением `Camera Driver for ov5647 and imx219` на форуме Orange
Pi. Совпадение с реальным источником подтверждается уникальными фрагментами:
`ov5647_sensor_vts`, `sensor_qsxga_regs`, HTS 2752, VTS 1974 и таблицей
2592×1944. При переносе были исправлены несовместимости и очевидные ошибки
старого кода.

Итоговый файл:

```text
bsp/drivers/vin/modules/sensor/ov5647.c
```

### 5.2. Что реализовано в драйвере

Драйвер содержит:

- проверку chip ID по регистрам `0x300a` и `0x300b`;
- ожидаемый идентификатор `0x5647`;
- 16-битный адрес регистра и 8-битные данные CCI;
- адрес сенсора `0x6c` в формате Allwinner CCI;
- последовательность включения питания, MCLK, PWDN и RESET;
- частоту MCLK 24 МГц;
- запуск потока через регистр `0x0100 = 0x01`;
- остановку потока через `0x0100 = 0x00`;
- настройку gain/exposure через регистры `0x3500`–`0x350b`;
- обновление VTS через `0x380e/0x380f`;
- RAW10 Bayer BGGR;
- MIPI CSI-2 D-PHY, две линии данных;
- три таблицы режимов;
- два логических имени драйвера: `ov5647` и `ov5647_2`.

### 5.3. Режимы изображения

| Размер | FPS | Pixel clock | MIPI bitrate | Назначение |
|---|---:|---:|---:|---|
| 1280×720 | 30 | 56 МГц | 280 Мбит/с | быстрый просмотр |
| 1920×1080 | 30 | 80 МГц | 400 Мбит/с | Full HD |
| 2592×1944 | 15 | 84 МГц | 420 Мбит/с | полное разрешение 5 Мп |

### 5.4. Поддержка двух имён

В драйвере зарегистрированы два CCI/I²C-драйвера:

```c
#define SENSOR_NAME   "ov5647"
#define SENSOR_NAME_2 "ov5647_2"
```

Это было сделано для будущей поддержки двух одинаковых камер. Сейчас активна
только `ov5647_2` на втором CSI-тракте.

### 5.5. Совместимость с API Linux 6.6

Учтены изменения API:

- сигнатура `i2c_driver.probe` для Linux 6.6;
- `remove()` возвращает `void` в новых ядрах;
- новый `v4l2_subdev_state`;
- новый формат `v4l2_mbus_config` для CSI-2;
- корректная регистрация и откат при ошибке второго экземпляра драйвера.

---

## 6. Изменения Kconfig и Makefile

### 6.1. `Kconfig`

Файл:

```text
bsp/drivers/vin/modules/sensor/Kconfig
```

Добавлено:

```kconfig
config SENSOR_OV5647
	tristate "use ov5647 driver"
	default n
```

### 6.2. Kernel Makefile

Файл:

```text
bsp/drivers/vin/modules/sensor/Makefile
```

Добавлено:

```make
obj-$(CONFIG_SENSOR_OV5647) += ov5647.o
```

### 6.3. Конфигурация Armbian

Файл:

```text
build/config/kernel/linux-sun60iw2-vendor.config
```

Добавлено:

```text
CONFIG_SENSOR_OV5647=m
```

Значение `m` означает сборку отдельного загружаемого модуля `ov5647.ko`, а не
встраивание драйвера непосредственно в `vmlinux`.

> В рабочем дереве `build` также есть отдельное пользовательское изменение в
> `0005-cubie-a7z-add-device-tree.patch`. Оно не относится к OV5647 и не должно
> случайно попадать в патч камеры.

---

## 7. Изменения Device Tree

### 7.1. Почему Device Tree обязателен

DTB сообщает ядру:

- какой сенсор физически установлен;
- на какой CCI/I²C-шине он находится;
- его адрес;
- номер MCLK;
- GPIO PWDN/RESET;
- к какому CSI/MIPI/VIN-тракту его подключить.

Без правильного DTB модуль может загрузиться, но не получит экземпляр устройства
для probe, либо поток будет направлен не в тот VIN.

### 7.2. Рабочая однокамерная конфигурация

Файл исходников:

```text
arch/arm64/boot/dts/allwinner/sun60i-a733-orangepi-zero3w.dts
```

Сделаны следующие изменения.

#### Первый сенсорный тракт отключён

```dts
sensor0_mname = "ov5647";
sensor0_twi_cci_id = <11>;
sensor0_twi_addr = <0x6c>;
status = "disabled";
```

#### Второй тракт настроен на OV5647

```dts
sensor2_mname = "ov5647_2";
sensor2_twi_cci_id = <9>;
sensor2_twi_addr = <0x6c>;
sensor2_mclk_id = <2>;
sensor2_pwdn = <&pio PE 10 GPIO_ACTIVE_HIGH>;
status = "okay";
```

#### Неиспользуемый `vinc0` отключён

```dts
vinc0_rear_sensor_sel = <0>;
vinc0_front_sensor_sel = <0>;
status = "disabled";
```

#### Рабочий `vinc8`

В штатном дереве `vinc8` уже направлен на `sensor2`:

```dts
vinc8_csi_sel = <1>;
vinc8_mipi_sel = <1>;
vinc8_isp_sel = <0>;
vinc8_rear_sensor_sel = <2>;
vinc8_front_sensor_sel = <2>;
status = "okay";
```

Именно поэтому рабочим узлом стал `/dev/video8`.

### 7.3. Быстрое создание DTB из установленного DTB

Именно этот способ применялся для быстрой и минимальной правки рабочего образа.

Установить `dtc`:

```bash
apt update
apt install -y device-tree-compiler
```

Декомпилировать исходный DTB:

```bash
KREL=$(uname -r)
DTB_DIR=/boot/dtb-$KREL/allwinner

dtc -I dtb -O dts \
  -o /root/sun60i-a733-orangepi-zero3w.original.dts \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.dtb"

cp /root/sun60i-a733-orangepi-zero3w.original.dts \
   /root/sun60i-a733-orangepi-zero3w.ov5647-single.dts
```

После редактирования свойств, перечисленных выше, собрать DTB:

```bash
dtc -I dts -O dtb \
  -o /root/sun60i-a733-orangepi-zero3w.ov5647-single.dtb \
  /root/sun60i-a733-orangepi-zero3w.ov5647-single.dts
```

`dtc` может вывести много предупреждений для декомпилированного vendor-DTB.
Перед установкой необходимо проверить, что команда завершилась успешно и новый
файл имеет разумный размер.

```bash
ls -lh /root/sun60i-a733-orangepi-zero3w.ov5647-single.dtb
sha256sum /root/sun60i-a733-orangepi-zero3w.ov5647-single.dtb
```

Контрольная сумма проверенного однокамерного DTB:

```text
5a8f531306248df25d562eb945d36e50c9ae06cdc226c28e29f180570c10d2ba
```

Установка:

```bash
cp -a \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.dtb" \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.before-next-change.dtb"

install -m 0644 \
  /root/sun60i-a733-orangepi-zero3w.ov5647-single.dtb \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.dtb"

sync
```

---

## 8. Как собрать `ov5647.ko` непосредственно на плате

Это быстрый способ собрать модуль под уже установленное ядро. Он не пересобирает
весь образ и ядро.

### 8.1. Подготовка

Камеру подключать и отключать только при полностью снятом питании.

Проверить ядро:

```bash
uname -r
```

Ожидается:

```text
6.6.98-vendor-sun60iw2
```

Установить инструменты:

```bash
apt update
apt install -y \
  build-essential \
  git \
  linux-headers-$(uname -r) \
  device-tree-compiler \
  v4l-utils \
  ffmpeg
```

### 8.2. Получение полного vendor-дерева

Полное дерево нужно потому, что `ov5647.c` включает внутренние заголовки из
`bsp/drivers/vin`, которых нет в обычном mainline-пакете headers.

```bash
cd /root

git clone \
  --filter=blob:none \
  --branch orange-pi-6.6-sun60iw2 \
  https://github.com/orangepi-xunlong/linux-orangepi.git \
  linux-orangepi-sun60iw2

cd /root/linux-orangepi-sun60iw2
git checkout 8a9be72c9006a87f786736b3aa4e2dfd971c1429
```

### 8.3. Передача адаптированного файла на плату

С рабочей машины:

```bash
DRIVER=/home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2/\
bsp/drivers/vin/modules/sensor/ov5647.c

scp "$DRIVER" \
  root@192.168.1.236:/root/linux-orangepi-sun60iw2/bsp/drivers/vin/modules/sensor/ov5647.c
```

### 8.4. Отдельный Kbuild только для OV5647

На плате:

```bash
cd /root/linux-orangepi-sun60iw2/bsp/drivers/vin/modules/sensor

printf '%s\n' 'obj-m := ov5647.o' > Kbuild
```

Файл `Kbuild` имеет приоритет над большим vendor-`Makefile`, поэтому будет собран
только `ov5647.ko`.

### 8.5. Сборка против текущего ядра

```bash
make -C /lib/modules/$(uname -r)/build \
  M="$PWD" \
  modules
```

Появится:

```text
ov5647.ko
```

Предупреждение о том, что ядро было собрано другой minor-версией GCC, допустимо,
если архитектура и ABI совпадают. Ошибки компиляции или `modpost` игнорировать
нельзя.

### 8.6. Проверка до установки

```bash
modinfo ./ov5647.ko
```

Проверить:

```bash
modinfo -F name ./ov5647.ko
modinfo -F vermagic ./ov5647.ko
modinfo -F depends ./ov5647.ko
modinfo -F alias ./ov5647.ko
```

Ожидается:

- имя: `ov5647`;
- `vermagic` начинается с `6.6.98-vendor-sun60iw2`;
- зависимость содержит `vin_io`;
- aliases содержат `i2c:ov5647` и `i2c:ov5647_2`.

Контрольная сумма проверенного модуля:

```text
14db777061a0177aaf8cc477eb197b826f88ba1fbcc24f4eaf75b89122236cb8
```

### 8.7. Установка модуля

```bash
KREL=$(uname -r)
DEST=/lib/modules/$KREL/kernel/bsp/drivers/vin/modules/sensor

install -d "$DEST"
install -m 0644 ./ov5647.ko "$DEST/ov5647.ko"
depmod -a "$KREL"
```

Проверка без перезагрузки:

```bash
modprobe vin_io
modprobe ov5647
modinfo ov5647
lsmod | grep -E 'ov5647|vin_io'
dmesg | tail -n 80
```

---

## 9. Автозагрузка модулей

Создан файл:

```text
/etc/modules-load.d/ov5647-camera.conf
```

Содержимое:

```text
ov5647
vin_v4l2
```

Команда создания:

```bash
printf '%s\n' ov5647 vin_v4l2 \
  > /etc/modules-load.d/ov5647-camera.conf
```

Проверка после перезагрузки:

```bash
lsmod | grep -E 'ov5647|vin_v4l2|vin_io'
dmesg | grep -E 'ov5647|detected chip|sensor id'
```

Рабочее сообщение:

```text
[ov5647]detected chip id 0x5647
```

Сообщение:

```text
ov5647: loading out-of-tree module taints kernel
```

не означает поломку. Оно сообщает, что загружен модуль, не входящий в
официальную сборку данного бинарного ядра.

---

## 10. Диагностика Media Controller и важность `--set-input=0`

После первой регистрации камера присутствовала в media graph, но связь между
сенсором и MIPI была неактивна:

```text
"ov5647_2":0 -> "sunxi_mipi.1":0 []
```

Из-за этого `vin_pipeline_try_format()` видел `VIN_IND_SENSOR == NULL`, а
установка формата завершалась `EINVAL`.

Топология проверялась так:

```bash
media-ctl -p -d /dev/media0
```

Связь можно было включить вручную для диагностики:

```bash
media-ctl -l '"ov5647_2":0 -> "sunxi_mipi.1":0 [1]'
```

Но правильный для vendor-драйвера способ — выбрать V4L2 input:

```bash
v4l2-ctl -d /dev/video8 --set-input=0
```

Внутри `sunxi-vin` ioctl `VIDIOC_S_INPUT` включает нужные media links, открывает
pipeline и заполняет указатель на sensor subdevice.

Поэтому **каждая новая сессия захвата должна сначала выполнять
`--set-input=0`**.

Проверка:

```bash
v4l2-ctl -d /dev/video8 --set-input=0
v4l2-ctl -d /dev/video8 --get-input
v4l2-ctl -d /dev/video8 --list-formats-ext
```

---

## 11. Захват RAW10

Выбрать вход и формат:

```bash
v4l2-ctl -d /dev/video8 \
  --set-input=0 \
  --set-fmt-video=width=1280,height=720,pixelformat=BG10
```

Захватить один RAW-кадр:

```bash
v4l2-ctl -d /dev/video8 \
  --stream-mmap=3 \
  --stream-count=1 \
  --stream-to=/tmp/ov5647-1280x720.raw
```

Ожидаемый размер:

```text
1280 × 720 × 2 = 1 843 200 байт
```

Каждый 10-битный Bayer pixel хранится в 16-битном слове, поэтому используется
два байта на пиксель.

Простая конвертация как `bayer_bggr16le` выглядит почти чёрной, потому что
полезные значения занимают младшие 10 бит. Для визуализации их нужно масштабировать
до 16-битного диапазона:

```bash
ffmpeg -hide_banner -loglevel error \
  -f rawvideo \
  -pixel_format bayer_bggr16le \
  -video_size 1280x720 \
  -i /tmp/ov5647-1280x720.raw \
  -vf "format=rgb48le,lutrgb=r='val*64':g='val*64':b='val*64'" \
  -frames:v 1 \
  /tmp/ov5647-raw.png
```

---

## 12. Захват обработанного цветного изображения через ISP

Гораздо удобнее запросить NV12. В этом случае встроенный ISP выполняет обработку
Bayer-данных.

```bash
v4l2-ctl -d /dev/video8 \
  --set-input=0 \
  --set-fmt-video=width=1280,height=720,pixelformat=NV12 \
  --stream-mmap=3 \
  --stream-skip=30 \
  --stream-count=1 \
  --stream-to=/tmp/ov5647-1280x720.nv12
```

Зачем `--stream-skip=30`:

- первые кадры после старта могут иметь неверную экспозицию;
- автоматике ISP нужно время стабилизировать gain/exposure/white balance;
- сохраняется кадр после примерно одной секунды работы.

Размер NV12:

```text
1280 × 720 × 1,5 = 1 382 400 байт
```

Конвертация в PNG:

```bash
ffmpeg -hide_banner -loglevel error -y \
  -f rawvideo \
  -pixel_format nv12 \
  -video_size 1280x720 \
  -i /tmp/ov5647-1280x720.nv12 \
  -frames:v 1 \
  /tmp/ov5647.png
```

---

## 13. Команда `capture-ov5647`

На плату установлен скрипт:

```text
/usr/local/bin/capture-ov5647
```

Исходник в рабочем каталоге:

```text
camera-ov5647/capture-ov5647
```

Использование:

```bash
capture-ov5647 /tmp/camera.png
```

Если имя файла не задано:

```bash
capture-ov5647
```

результат сохраняется в:

```text
/tmp/ov5647.png
```

Скрипт выполняет весь обязательный порядок:

1. выбирает `/dev/video8`;
2. вызывает `--set-input=0`;
3. задаёт 1280×720 NV12;
4. пропускает 30 кадров;
5. сохраняет один кадр;
6. конвертирует его в PNG;
7. удаляет временный NV12.

Переопределить устройство можно переменной:

```bash
OV5647_DEVICE=/dev/video8 capture-ov5647 /tmp/camera.png
```

---

## 14. Локальный веб-просмотр

На плату установлен:

```text
/usr/local/bin/ov5647-web
```

Исходник:

```text
camera-ov5647/ov5647-web
```

Запуск:

```bash
ov5647-web start
```

Открыть в браузере:

```text
http://192.168.1.236:8080/
```

Управление:

```bash
ov5647-web status
ov5647-web restart
ov5647-web stop
```

Сервис состоит из двух процессов:

- цикл делает новый PNG примерно раз в 2–3 секунды;
- `python3 -m http.server` раздаёт страницу и текущий `camera.png`.

Рабочий каталог во время запуска:

```text
/run/ov5647-web
```

Лог:

```text
/run/ov5647-web/ov5647-web.log
```

Проверка процессов:

```bash
cat /run/ov5647-web/capture.pid
cat /run/ov5647-web/server.pid
ps -fp "$(cat /run/ov5647-web/capture.pid)"
ps -fp "$(cat /run/ov5647-web/server.pid)"
```

Порт можно изменить:

```bash
OV5647_WEB_PORT=8090 ov5647-web start
```

Это не непрерывный MJPEG/H.264 поток, а автоматически обновляемые снимки. Такой
вариант был выбран как наиболее устойчивый для текущего vendor V4L2 MPlane-
драйвера. Для настоящего видео лучше отдельно настроить GStreamer или аппаратный
кодировщик Allwinner после стабилизации драйвера.

---

## 15. Проверка после перезагрузки

### 15.1. Проверить модуль

```bash
lsmod | grep -E 'ov5647|vin_v4l2|vin_io'
modinfo ov5647
```

### 15.2. Проверить обнаружение сенсора

```bash
dmesg | grep -E 'ov5647|detected chip|sensor id'
```

Ожидается одна строка обнаружения:

```text
[ov5647]detected chip id 0x5647
```

### 15.3. Проверить устройства

```bash
ls -l /dev/video* /dev/media*
v4l2-ctl --list-devices
```

Ожидается:

```text
/dev/video8
/dev/media0
```

Сообщение `Cannot open device /dev/video0` от команды перечисления не является
ошибкой камеры: в однокамерной конфигурации активен только `video8`.

### 15.4. Проверить runtime Device Tree

```bash
tr -d '\0' \
  </proc/device-tree/soc@3000000/vind@5800800/sensor@5812000/status

tr -d '\0' \
  </proc/device-tree/soc@3000000/vind@5800800/sensor@5812020/status
```

Ожидается:

```text
disabled
okay
```

Имя второго сенсора:

```bash
tr -d '\0' \
  </proc/device-tree/soc@3000000/vind@5800800/\
sensor@5812020/sensor2_mname
```

Ожидается:

```text
ov5647_2
```

---

## 16. Как собрать полноценный kernel package через Armbian

Быстрая сборка внешнего `.ko` удобна для экспериментов. Для воспроизводимого
образа изменения лучше оформить как патч Armbian.

### 16.1. Требования к build host

Рекомендуется Ubuntu 24.04 или Armbian, минимум 8 ГБ RAM и около 50 ГБ свободного
места.

```bash
git clone https://github.com/armbian/build.git
cd build
```

### 16.2. Создание патча из рабочего kernel tree

В kernel tree необходимо пометить новый файл для отображения в `git diff`, не
добавляя commit:

```bash
cd /home/artm1904/Program/Robot/os/linux-orangepi-sun60iw2

git add -N bsp/drivers/vin/modules/sensor/ov5647.c

PATCH_DIR=/home/artm1904/Program/Robot/os/build/userpatches/kernel/archive/\
sun60iw2-opi-vendor

mkdir -p "$PATCH_DIR"

git diff -- \
  bsp/drivers/vin/modules/sensor/ov5647.c \
  bsp/drivers/vin/modules/sensor/Kconfig \
  bsp/drivers/vin/modules/sensor/Makefile \
  arch/arm64/boot/dts/allwinner/sun60i-a733-orangepi-zero3w.dts \
  > "$PATCH_DIR/0100-orangepizero3w-add-ov5647.patch"
```

### 16.3. Пользовательская kernel config

```bash
cd /home/artm1904/Program/Robot/os/build

cp config/kernel/linux-sun60iw2-vendor.config \
   userpatches/linux-sun60iw2-vendor.config
```

Убедиться, что присутствует:

```text
CONFIG_SENSOR_OV5647=m
```

### 16.4. Сборка kernel packages

```bash
./compile.sh kernel \
  BOARD=orangepizero3w \
  BRANCH=vendor
```

Результаты следует искать в:

```text
output/debs/
```

Перед установкой нового полного ядра нужно сохранить `/boot`, DTB и рабочие
модули. Установка kernel `.deb` может изменить строку `uname -r`, поэтому старый
`ov5647.ko` после этого использовать нельзя — его нужно собрать заново.

---

## 17. Откат к исходному состоянию

### 17.1. Восстановить исходный DTB

```bash
KREL=$(uname -r)
DTB_DIR=/boot/dtb-$KREL/allwinner

install -m 0644 \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.pre-ov5647-20260811.dtb" \
  "$DTB_DIR/sun60i-a733-orangepi-zero3w.dtb"
```

### 17.2. Убрать автозагрузку

```bash
mv /etc/modules-load.d/ov5647-camera.conf \
   /etc/modules-load.d/ov5647-camera.conf.disabled
```

### 17.3. Убрать модуль из активного дерева

```bash
KREL=$(uname -r)

mkdir -p /root/ov5647-backup

mv /lib/modules/$KREL/kernel/bsp/drivers/vin/modules/sensor/ov5647.ko \
   /root/ov5647-backup/ov5647.ko

depmod -a "$KREL"
sync
reboot
```

### 17.4. Аварийное восстановление при отсутствии загрузки

Если плата не появляется в сети, нужен UART serial console или доступ к карте
памяти с другого Linux-компьютера. На смонтированном разделе необходимо заменить
активный DTB сохранённой копией.

---

## 18. Что происходило с двумя камерами

Для двух OV5647 был подготовлен DTB, в котором одновременно включались:

- `sensor0` → `ov5647`, CCI 11, MCLK1, PWDN PE6;
- `sensor2` → `ov5647_2`, CCI 9, MCLK2, PWDN PE10;
- `vinc0` и `vinc8`.

При одном из запусков обе камеры успешно вернули chip ID `0x5647` и появились
`/dev/video0` и `/dev/video8`. Однако холодная загрузка с двумя подключёнными
модулями оказалась нестабильной. Поэтому двухкамерный DTB не рекомендуется
активировать без UART-консоли и измерения линий питания.

Сохранённый файл:

```text
sun60i-a733-orangepi-zero3w.dual-ov5647-20260811.dtb
```

Вероятные направления дальнейшей диагностики:

- общий ток камер при старте;
- последовательность включения AVDD/DVDD/IOVDD;
- состояние PWDN обоих сенсоров в U-Boot и до probe;
- конфликты GPIO PE6/PE10;
- MCLK1/MCLK2;
- правильность разводки двух CSI-разъёмов;
- поведение PMIC при пусковом токе;
- наличие зависания до Linux через UART boot log.

---

## 19. Аппаратная безопасность

1. Камеру и FPC-шлейф подключать только при физически отключённом питании.
2. После `poweroff` вынуть кабель питания и подождать минимум 20–30 секунд.
3. Проверять, что шлейф вставлен ровно и фиксатор закрыт.
4. Не ориентироваться только на цвет синей стороны шлейфа: смотреть на открытые
   контакты и конструкцию конкретного разъёма.
5. Если с камерой не загорается даже индикатор питания — немедленно отключить
   питание. Это похоже на замыкание, неверный шлейф, перекос контактов или
   перегрузку питания, а не на ошибку V4L2.
6. Не повторять много раз запуск при подозрении на короткое замыкание.
7. Для двух камер сначала получить стабильный старт каждой камеры отдельно.

---

## 20. Частые ошибки и их смысл

### `Module ov5647 not found`

Не выполнен `depmod`, модуль установлен не под текущий `uname -r` или отсутствует
в `/lib/modules/...`.

```bash
depmod -a
find /lib/modules/$(uname -r) -name 'ov5647.ko*'
```

### `invalid module format`

Не совпадает `vermagic` или модуль собран для другого ядра/архитектуры.

```bash
uname -r
modinfo -F vermagic ./ov5647.ko
dmesg | tail -n 30
```

### `Unknown symbol ...`

Не загружена зависимость `vin_io`, не совпадает vendor ABI или отсутствуют
символы в `Module.symvers`.

```bash
modprobe vin_io
modprobe ov5647
dmesg | tail -n 80
```

### `chip found is not an target chip`

Не удалось прочитать `0x5647`. Проверить питание, шлейф, CCI ID, адрес, MCLK,
PWDN и правильный CSI-разъём.

### Формат `0×0`, `VIDIOC_S_FMT: Invalid argument`

Обычно не был выбран вход и media pipeline не связал sensor subdevice.

```bash
v4l2-ctl -d /dev/video8 --set-input=0
```

### RAW выглядит чёрным

10-битные значения лежат в 16-битных словах без растяжения яркости. Использовать
ISP/NV12 либо умножить значения на 64 перед выводом.

### `failed to get vipp16 IRQ resource`

Это сообщение vendor-драйвера наблюдалось и при рабочем захвате. Для текущего
`vinc8` оно не оказалось критичным.

### `v4l2 sub device scaler get_selection error`

Vendor ISP/scaler не реализует или не полностью реализует часть selection API.
Сообщение наблюдалось при успешном захвате, но его нельзя игнорировать при
появлении реальных ошибок формата или потока.

---

## 21. Что читать и в каком порядке

### Уровень 1: основы Linux и аппаратуры

Искать и изучать:

- `Linux kernel module basics`;
- `I2C 7-bit vs 8-bit address`;
- `MIPI CSI-2 D-PHY lanes clock lane`;
- `Bayer BGGR RAW10 debayer`;
- `camera exposure gain frame length VTS HTS`;
- `FPC connector contact orientation`.

### Уровень 2: Device Tree

Темы:

- DTS, DTSI и DTB;
- `compatible`, `status`, `reg`, phandle;
- GPIO polarity;
- clocks и regulators;
- endpoint/port graph bindings.

Документация:

- [Devicetree basics](https://devicetree-specification.readthedocs.io/en/stable/devicetree-basics.html)
- [DTS source format](https://devicetree-specification.readthedocs.io/en/v0.2/source-language.html)

Практические команды:

```bash
dtc -I dtb -O dts input.dtb -o output.dts
dtc -I dts -O dtb input.dts -o output.dtb
fdtdump file.dtb
fdtget file.dtb /path/to/node property
```

### Уровень 3: Kbuild и модули ядра

Темы:

- `obj-m`, `obj-$(CONFIG_...)`;
- `Kconfig`;
- `M=$PWD`;
- `Module.symvers`;
- `vermagic`;
- exported symbols;
- `modprobe`, `depmod`, `modinfo`.

Документация:

- [Building External Modules](https://docs.kernel.org/next/kbuild/modules.html)
- [Kbuild](https://docs.kernel.org/kbuild/kbuild.html)
- [Kernel Build System](https://docs.kernel.org/next/kbuild/index.html)

### Уровень 4: V4L2 и Media Controller

Темы:

- V4L2 video node;
- V4L2 subdevice;
- media entity, pad и link;
- pixel format/FourCC;
- streaming buffers и MMAP;
- controls: exposure, gain, white balance;
- multi-planar capture.

Документация:

- [Media Controller API](https://docs.kernel.org/userspace-api/media/mediactl/media-controller.html)
- [Using camera sensor drivers](https://docs.kernel.org/userspace-api/media/drivers/camera-sensor.html)
- [Writing camera sensor drivers](https://docs.kernel.org/driver-api/media/camera-sensor.html)

Инструменты:

```bash
v4l2-ctl --help-all
media-ctl --help
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video8 --all
media-ctl -p -d /dev/media0
```

### Уровень 5: сам OV5647

Искать:

- `OV5647 datasheet register map`;
- `OV5647 0x300a 0x300b chip id`;
- `OV5647 0x0100 streaming`;
- `OV5647 PLL 0x3034 0x3035 0x3036`;
- `OV5647 exposure registers 0x3500`;
- `OV5647 output size 0x3808`;
- `OV5647 MIPI timing 0x4837`.

Полезно сравнивать:

```text
drivers/media/i2c/ov5647.c
bsp/drivers/vin/modules/sensor/ov5648_mipi.c
bsp/drivers/vin/modules/sensor/imx219.c
bsp/drivers/vin/modules/sensor/ov5647.c
```

### Уровень 6: Armbian Build Framework

Документация:

- [Armbian build preparation](https://docs.armbian.com/Developer-Guide_Build-Preparation/)
- [Armbian user configurations and patches](https://docs.armbian.com/Developer-Guide_User-Configurations/)

Искать:

- `Armbian userpatches kernel patch`;
- `Armbian build kernel only`;
- `Armbian custom kernel config`;
- `Armbian BOARD BRANCH vendor compile.sh`.

### Уровень 7: следующий практический шаг

После стабильной работы одной камеры разумный порядок дальнейших работ:

1. Настроить UART serial console и сохранить полный boot log.
2. Измерить напряжения камеры при холодном старте.
3. Добиться стабильной работы 720p, затем 1080p и 5 Мп.
4. Проверить длительный непрерывный захват.
5. Настроить GStreamer/MJPEG/H.264.
6. Только после этого возвращаться к двум камерам.
7. Для двух камер включать тракты по одному и проверять media graph после каждого
   изменения.

---

## 22. Карта файлов проекта

| Файл | Назначение |
|---|---|
| `ov5647.ko` | собранный модуль под `6.6.98-vendor-sun60iw2` |
| `ov5647-single-csi2-sun60i-a733-orangepi-zero3w.dtb` | рабочий DTB для одной камеры на втором CSI |
| `ov5647-single-csi2-sun60i-a733-orangepi-zero3w.dts` | его текстовое представление |
| `ov5647-dual-sun60i-a733-orangepi-zero3w.dtb` | экспериментальный DTB для двух камер |
| `original-sun60i-a733-orangepi-zero3w.dtb` | сохранённый исходный DTB |
| `capture-ov5647` | захват одного PNG |
| `ov5647-web` | локальная веб-страница с автообновлением |
| `ov5647-1280x720.raw` | тестовый RAW10 кадр |
| `ov5647-1280x720.nv12` | тестовый обработанный кадр NV12 |
| `ov5647-latest.png` | контрольный цветной PNG |

---

## 23. Краткая рабочая памятка

```bash
# Проверить камеру
dmesg | grep ov5647
v4l2-ctl --list-devices

# Сделать снимок
capture-ov5647 /tmp/camera.png

# Запустить веб-просмотр
ov5647-web start

# Остановить веб-просмотр
ov5647-web stop

# Посмотреть media graph
media-ctl -p -d /dev/media0

# Проверить модуль
modinfo ov5647
lsmod | grep ov5647

# Посмотреть ошибки текущей загрузки
dmesg -T | grep -E 'ov5647|sunxi:vin|mipi|csi'
```

Главный рабочий URL:

```text
http://192.168.1.236:8080/
```
