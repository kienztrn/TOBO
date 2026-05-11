
============================================================
TOBO VIETSUB v1.6.6 - AUTO UPDATE IN-PLACE
============================================================

Ban nay them auto-update dung kieu:
- Bam "Cap nhat" -> app tai file main.zip tu GitHub.
- Tai xong -> app hoi co cai ngay khong.
- Dong y -> app tu ghi de file app moi.
- GIU NGUYEN:
  .venv
  thu vien da cai
  output
  temp
  updates
  build/dist/release

Nghia la KHONG can xoa ban cu, KHONG can cai thu vien lai tu dau.

Cach publish ban moi len GitHub:
1. Sua app/code.
2. Tang CURRENT_VERSION trong app.py.
3. Tang version trong update_manifest.json.
4. Bam PUBLISH_UPDATE_TO_GITHUB.bat hoac PUSH_TO_GITHUB.bat.
5. May khac bam "Cap nhat" trong app la tu len ban moi.

Luu y:
- Ban cu truoc v1.6.0 chua co auto-apply, nen lan nay co the phai tai tay 1 lan.
- Tu v1.6.0 tro di, cac lan sau bam "Cap nhat" se tu tai va tu ap dung.
- update_manifest.json dang tro den:
  https://github.com/kienztrn/TOBO/archive/refs/heads/main.zip
  Nen khong can GitHub Releases nua, chi can push code len main.


TOBO VIETSUB - WINDOWS - FUTURE UI + SRT

BAN NAY DA THEM:
- Doi ten app thanh: TOBO VietSub.
- Nang cap giao dien dark neon/future, nhin hien dai hon ban pastel cu.
- Nut co hieu ung hover/click, bam co am thanh nhe tren Windows.
- Co checkbox bat/tat Am click.
- O ban dich chi hien van ban dich sach, KHONG kem timestamp.
- Them tuy chon xuat file: TXT, SRT, TXT + SRT.
- Them nut Xuat SRT rieng sau khi xu ly xong.
- Van giu nut Kiem tra cap nhat qua GitHub manifest.

CACH CHAY SOURCE:
1. Giai nen ZIP.
2. Bam install_windows.bat de cai thu vien.
3. Bam run_app.bat de mo app.

CACH BUILD EXE:
1. Bam BUILD_EXE_1_CLICK.bat.
2. File se nam tai:
   release\TOBO_VietSub\TOBO_VietSub.exe

CACH TAO PORTABLE:
- Bam MAKE_PORTABLE_RELEASE.bat hoac BUILD_PORTABLE_RELEASE.bat.

XUAT FILE:
- TXT: transcript text.
- SRT: subtitle dung cho video editor.
- TXT + SRT: xuat ca hai.

LUU Y:
- Neu chon dich, o phai chi hien text dich sach.
- SRT van giu timestamp vi file subtitle bat buoc can timestamp.
- Lan dau dung model Whisper co the can Internet de tai model.
- Neu file video/audio la codec la, cai FFmpeg:
  winget install Gyan.FFmpeg

GITHUB UPDATE:
- update_config.json da tro den:
  https://raw.githubusercontent.com/kienztrn/TOBO/main/update_manifest.json
- Muon nut Cap nhat tai ban moi that, tao GitHub Release va upload file TOBO_VietSub_Portable.zip.

BAN 1.5.0 - VIDEO BACKGROUND:
- Da them background_config.json.
- Giao diện đã bỏ nền video để nhìn sạch và đỡ rối mắt.
- Phần header bên phải dùng hiệu ứng sparkle/future build theo tông của logo mèo.
- Có checkbox "Sparkle FX" để bật/tắt hiệu ứng lấp lánh.
- Video nen duoc cat frame nhe de tranh lag, khong phat full HD truc tiep nhu game engine.


BAN v1.6.2:
- Giao diện sáng, sạch kiểu Apple/AI tool hiện đại.
- Bỏ nền video rối mắt, giữ Sparkle FX nhẹ theo logo.
- Auto-update in-place: giữ .venv, output, temp, updates, không tải lại thư viện.

BAN v1.6.3:
- Them nut cai dat goc tren phai dang icon vuong 3 gach: ☰.
- Cho phep doi ngon ngu app: Tieng Viet, English, Korean, Chinese.
- Them 9 bang mau giao dien: Peach, Apple Light, Pink Neon, Blue Cloud, Golden, Shopee Peach, Coffee Gold...
- Doi theme ap dung ngay, khong xoa .venv, khong tai lai thu vien.
- Auto-update in-place van giu nguyen output/temp/updates/.venv.

BAN v1.6.4:
- Them theme moi: 10. Dark Orange, nen toi + cam.
- Sua ngon ngu app: doi ngon ngu se doi dong bo UI chinh, nut bam, combobox, status, dialog va cua so cai dat.
- Cac lua chon ngon ngu nguon/dich/model/thiet bi cung hien theo ngon ngu app.
- Auto-update in-place van giu .venv, thu vien, output, temp va updates.

BAN v1.6.5:
- Them tuy chon Delay <#s#> de chen lenh nghi vao ban dich.
- Delay duoc tinh tu timestamp cua ban goc: segment duration + khoang lang giua cac cau.
- Xuat them file *_voice_timing.txt de dua vao tool doc/giong noi canh nhip theo video.
- Them nut "Xuat Voice TXT".

BAN v1.6.6:
- Them lua chon Phong cach dich: Tu nhien, Hai huoc, Nghiem tuc, Kinh di, Lang man, Khoa hoc vien tuong, Hoat hinh vui nhon, Hanh dong.
- Them o Ten folder xuat: file TXT/SRT/Voice TXT se duoc gom vao output/<ten_folder>.
- Them nut Cach dung / Ban cap nhat trong cua so Cai dat.
- Giu auto-update in-place: khong xoa .venv, khong cai lai thu vien, khong dong output/temp/updates.


V1.6.9 HOTFIX:
- Bo chu VIDEO va text debug frames tren header video.
- Doi nut Updates thanh nut Ung ho.
- Bam Ung ho se mo popup QR placeholder. Sau nay dat ma QR vao assets/support_qr.png.
- Fix layout nut header de khong bi cat hien thi.


V1.7.0:
- Them model Turbo - large-v3-turbo.
- Dat Turbo lam model mac dinh de xu ly nhanh hon.
- Neu alias turbo bi loi, app tu fallback sang model CTranslate2 tren Hugging Face.


V1.7.1:
- Nâng cấp bộ phong cách dịch theo yêu cầu: Giữ nghĩa sát, Dịch tự nhiên, Viral/TikTok, Phim hoạt hình, Lồng tiếng, Hài bựa nhẹ, Lịch sự, Như người bản xứ.
- Vẫn giữ Whisper Turbo mặc định và auto-update in-place, không xóa .venv/thư viện/output.

v1.7.2:
- Them nut Kiem tra he thong: Python, faster-whisper, FFmpeg, model cache, Internet, GPU/CUDA, output.
- Them tuy chinh Voice Delay: toc do doc cham/vua/nhanh, delay toi thieu, delay toi da, lam tron delay, bo delay nho hon 0.2s.
- Sap xep lai khu dieu khien cho gon hon va lam mem visual card.


BAN v1.7.4:
- Sua nut cai dat: bam ☰ de thu/phong panel cai dat ngay trong app.
- Khong mo cua so popup rieng khi bam cai dat nua.
- Giu auto-update in-place, khong xoa .venv/thu vien/output/temp/updates.


BAN 1.7.8:
- Bo o SYSTEM STATUS.
- Thay bang o Bat dau xu ly gon hon nam ngay tren phan Van ban goc/Ban dich.
- Loader van hien dang overlay giua app khi xu ly.


BAN v1.8.1:
- Them preset 🎭 Cartoon Mode.
- Tu set Phong cach dich = Dich phim hoat hinh.
- Tu set Toc do doc = Vua.
- Tu set Delay = 0.15 den 2.00s.
- Tu set SRT toi da 2 dong.
