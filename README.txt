
============================================================
TOBO VIETSUB v1.6.0 - AUTO UPDATE IN-PLACE
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
