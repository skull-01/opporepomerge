; Tauri NSIS PREINSTALL hook for Kodi Oppo External Player Configurator.
;
; This is the SINGLE old-version prompt for the installer. The stock Tauri NSIS
; reinstall page -- which used to detect a prior NSIS install and offer to remove
; it -- was removed from the vendored installer.nsi (ENH #334) so the user never
; sees two prompts. This hook now detects BOTH a prior NSIS install of this
; product (our own uninstall key ${UNINSTKEY}) AND a parallel MSI install (which
; the reinstall page never saw), and offers to remove whichever exist behind one
; confirmation.
;
; It runs at the top of the install Section -- before any files are copied and
; before the new uninstall key is written -- so the registry still reflects the
; PRIOR install on an upgrade. RestorePreviousInstallLocation (in .onInit) has
; already pointed $INSTDIR at the prior install directory.
;
; NOTE: not unit-testable. `makensis` validates this compiles into the installer
; at build time (the configurator CI runs `tauri build` only on a configurator-v*
; tag; it is also built locally before release). The detect/remove behaviour and
; the single-prompt UX are operator (Phase-C) verified on a real Windows host
; with a previous version installed.

!macro NSIS_HOOK_PREINSTALL
  Push $0
  Push $1
  Push $2
  Push $3
  Push $4

  ; $0 = UninstallString of a prior NSIS install of this product ("" if none).
  ReadRegStr $0 SHCTX "${UNINSTKEY}" "UninstallString"

  ; $1 = uninstall subkey (ProductCode GUID) of a parallel MSI install ("" if none).
  ; Our own NSIS key is named ${PRODUCTNAME}; skip it so it is never read as MSI.
  StrCpy $1 ""
  StrCpy $2 0
  oppo_msi_scan:
    EnumRegKey $3 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" $2
    StrCmp $3 "" oppo_msi_done
    IntOp $2 $2 + 1
    StrCmp $3 "${PRODUCTNAME}" oppo_msi_scan
    ReadRegStr $4 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$3" "DisplayName"
    StrCmp $4 "${PRODUCTNAME}" 0 oppo_msi_scan
    ReadRegStr $4 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$3" "Publisher"
    StrCmp $4 "${MANUFACTURER}" 0 oppo_msi_scan
    StrCpy $1 $3
    Goto oppo_msi_done
  oppo_msi_done:

  ; Nothing prior -> fresh install, no prompt.
  StrCmp $0 "" 0 oppo_have_prior
  StrCmp $1 "" oppo_pre_done

  oppo_have_prior:
  MessageBox MB_YESNO|MB_ICONQUESTION "A previous version of ${PRODUCTNAME} was found.$\r$\n$\r$\nRemove it before installing? (Recommended)" IDNO oppo_pre_done

    ; Remove a prior NSIS install: run its uninstaller silently and in place.
    ; _?=<dir> keeps it synchronous in the install dir; /S suppresses its UI and
    ; leaves the "remove data" option unchecked, so app settings are preserved.
    StrCmp $0 "" oppo_skip_nsis
      ReadRegStr $4 SHCTX "${MANUPRODUCTKEY}" ""
      StrCmp $4 "" 0 oppo_nsis_dir_ok
        StrCpy $4 "$INSTDIR"
      oppo_nsis_dir_ok:
      ExecWait '$0 /S _?=$4' $2
    oppo_skip_nsis:

    ; Remove a parallel MSI install silently.
    StrCmp $1 "" oppo_skip_msi
      ExecWait 'msiexec /x $1 /qn /norestart' $2
    oppo_skip_msi:

  oppo_pre_done:
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0
!macroend
