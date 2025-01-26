**Added:**

* Added `gamryloader.Gamryloader` for loading Gamry Instruments Framework software `*.DTA` files.
* Added `BaseLoader.metadata` which should contain the metadata inferred from the header as a dic.
* Added `BaseLoader.column_headers`, `BaseLoader.column_header_lines`.
* Added `BaseLoader.delimiter`, which uses `clevercsv` to determine the delimiter from the combined `BaseLoader.data` and `BaseLoader.column_header_lines`.
* Added `BaseLoader.decimal` which determines the decimal separator from `BaseLoader.data`.
* Added `BaseLoader.column_header_names`, which flattens the column header names found in `BaseLoader.column_headers`.
* Added the helper method `BaseLoader._validate_digits` for `BaseLoader.decimal`.

**Changed:**

* Changed name `csvloader.CSVloader` to `baseloader.BaseLoader`.
* Changed create `csvloader.BaseLoader.df` from various  `BaseLoader`` properties.

**Deprecated:**

* Deprecated `BaseLoader.augment`, `BaseLoader.column_names`, `EClabloader.df` and `EClabloader.decimal`.

