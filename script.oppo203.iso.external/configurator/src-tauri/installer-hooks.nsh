; Tauri NSIS PREINSTALL hook for OppoKodiAddon Configurator.
;
; Before the new files are written, detect every previously-installed version of the configurator
; -- our own (NSIS) install via the uninstall key, plus any MSI install of the same product in the
; per-machine uninstall registry -- and offer, in one prompt, to remove them all, then proceed.
;
; This implements the "check for old versions, offer to delete all old versions, then install"
; request. Tauri's built-in reinstall page also offers to remove the primary detected install;
; this hook additionally guarantees a parallel MSI install is cleared when the user opts in.
;
; NOTE: not unit-testable -- `makensis` validates that this compiles into the installer at build
; time; the actual detect/remove behaviour is operator (Phase-C) verified against a real machine.

!macro NSIS_HOOK_PREINSTALL
  Push $0
  Push $1
  Push $2
  Push $3
  Push $4

  ; $0 = our NSIS UninstallString (empty if not installed); $1 = MSI ProductCode (empty if none).
  ReadRegStr $0 SHCTX "${UNINSTKEY}" "UninstallString"
  StrCpy $1 ""
  StrCpy $2 0
  oppo_msi_scan:
    EnumRegKey $3 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall" $2
    StrCmp $3 "" oppo_msi_done
    IntOp $2 $2 + 1
    ReadRegStr $4 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$3" "DisplayName"
    StrCmp $4 "${PRODUCTNAME}" 0 oppo_msi_scan
    ReadRegStr $4 HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\$3" "Publisher"
    StrCmp $4 "${MANUFACTURER}" 0 oppo_msi_scan
    StrCpy $1 $3
    Goto oppo_msi_done
  oppo_msi_done:

  ; Nothing previously installed -> just proceed.
  StrCmp "$0$1" "" oppo_pre_done

  MessageBox MB_YESNO|MB_ICONQUESTION "One or more previously installed versions of ${PRODUCTNAME} were found.$\r$\n$\r$\nRemove all old versions before installing? (Recommended)" IDNO oppo_pre_done

  ; Remove our NSIS install silently (the Tauri uninstaller honours /S).
  StrCmp $0 "" oppo_pre_msi
    ReadRegStr $0 SHCTX "${UNINSTKEY}" "QuietUninstallString"
    StrCmp $0 "" 0 oppo_pre_nsis_run
      ReadRegStr $0 SHCTX "${UNINSTKEY}" "UninstallString"
      StrCpy $0 "$0 /S"
    oppo_pre_nsis_run:
      ExecWait '$0' $2

  oppo_pre_msi:
  ; Remove a parallel MSI install silently (the subkey name is the ProductCode GUID).
  StrCmp $1 "" oppo_pre_done
    ExecWait 'msiexec /x $1 /qn /norestart' $2

  oppo_pre_done:
  Pop $4
  Pop $3
  Pop $2
  Pop $1
  Pop $0
!macroend
