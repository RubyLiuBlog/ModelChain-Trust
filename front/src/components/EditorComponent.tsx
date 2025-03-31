"use client";

import {
  MDXEditor,
  MDXEditorMethods,
  headingsPlugin,
  listsPlugin,
  quotePlugin,
  thematicBreakPlugin,
  markdownShortcutPlugin,
} from "@mdxeditor/editor";
import { FC, useState } from "react";

interface EditorProps {
  value?: string;
  initialValue?: string;
  editorRef?: React.MutableRefObject<MDXEditorMethods | null>;
}

/**
 * Extend this Component further with the necessary plugins or props you need.
 * proxying the ref is necessary. Next.js dynamically imported components don't support refs.
 */
const Editor: FC<EditorProps> = ({ value, editorRef, initialValue = "" }) => {
  const [markdownValue, setMarkdownValue] = useState(value || initialValue);
  const handleChange = (value: string) => {
    setMarkdownValue(value);
  };

  return (
    <MDXEditor
      className="dark-theme dark-editor"
      onChange={(v) => handleChange(v)}
      ref={editorRef}
      markdown={markdownValue}
      plugins={[
        headingsPlugin(),
        quotePlugin(),
        listsPlugin(),
        thematicBreakPlugin(),
        markdownShortcutPlugin(),
      ]}
    />
  );
};

export default Editor;
