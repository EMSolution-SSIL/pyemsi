import type { InstallationSlideContent } from "./types";

export const installationSlideJapaneseContent: InstallationSlideContent = {
    language: "ja",
    checklistItems: [
        {
            id: "download",
            label: "最新の Windows インストーラーをダウンロード",
            detail: "GitHub Releases から最新の pyemsi セットアップファイルを取得します。",
        },
        {
            id: "install",
            label: "pyemsi GUI アプリケーションをインストール",
            detail: "インストーラーを実行し、オプションを確認してセットアップを完了します。",
        },
        {
            id: "pyemsol",
            label: "pyemsi 内に pyemsol をインストール",
            detail: "内蔵の IPython ターミナルで %pip を使ってホイールをインストールします。",
        },
        {
            id: "verify",
            label: "インストール内容を確認",
            detail: "pyemsi を起動し、ターミナルを開いて pyemsol が使えることを確認します。",
        },
    ],
    scenes: [
        {
            type: "checklist",
            id: "checklist-download-pending",
            checklistItemId: "download",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-download",
            checklistItemId: "download",
            assetSrc: "downloading-pyemsi.mp4",
            durationInFrames: 290,
        },
        {
            type: "checklist",
            id: "checklist-download-complete",
            checklistItemId: "install",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-install",
            checklistItemId: "install",
            assetSrc: "installing-pyemsi.mp4",
            durationInFrames: 1020,
        },
        {
            type: "checklist",
            id: "checklist-install-complete",
            checklistItemId: "pyemsol",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-pyemsol",
            checklistItemId: "pyemsol",
            assetSrc: "installing-pyemsol.mp4",
            durationInFrames: 810,
        },
        {
            type: "checklist",
            id: "checklist-pyemsol-complete",
            checklistItemId: "verify",
            durationInFrames: 120,
        },
        {
            type: "video",
            id: "video-verify",
            checklistItemId: "verify",
            assetSrc: "verify-pyemsol.mp4",
            durationInFrames: 920,
        },
    ],
};