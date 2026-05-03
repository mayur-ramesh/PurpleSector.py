import { useEffect } from 'react';

const BASE_TITLE = 'PurpleSector — F1 Analytics';

const useDocumentTitle = (title) => {
  useEffect(() => {
    document.title = title ? `${title} | PurpleSector` : BASE_TITLE;
    return () => {
      document.title = BASE_TITLE;
    };
  }, [title]);
};

export default useDocumentTitle;
