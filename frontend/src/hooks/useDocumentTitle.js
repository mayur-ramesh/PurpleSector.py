import { useEffect } from 'react';

const BASE_TITLE = '@purplesector.py — F1 Analytics';

const useDocumentTitle = (title) => {
  useEffect(() => {
    document.title = title ? `${title} | @purplesector.py` : BASE_TITLE;
    return () => {
      document.title = BASE_TITLE;
    };
  }, [title]);
};

export default useDocumentTitle;
