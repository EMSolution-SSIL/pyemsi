"""Custom delegate for property tree widget with editable cells."""

from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QColorDialog,
    QSlider,
    QStyleOptionViewItem,
    QWidget,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, QModelIndex, QEvent, QRect
from PySide6.QtGui import QColor, QPalette


class SliderLineEditWidget(QWidget):
    """Composite widget combining QSlider and QSpinBox/QDoubleSpinBox.

    Provides two synchronized input methods:
    - Slider for continuous dragging adjustment
    - SpinBox for precise numeric input

    Both widgets stay synchronized bidirectionally.
    """

    def __init__(
        self,
        min_val,
        max_val,
        steps=100,
        orientation=Qt.Orientation.Horizontal,
        decimals=2,
        parent=None,
    ):
        """Initialize composite slider+spinbox widget.

        Args:
            min_val: Minimum value
            max_val: Maximum value
            steps: Number of discrete steps for slider (applies to both int and float)
            orientation: Qt.Horizontal or Qt.Vertical for slider
            decimals: Number of decimal places for float spinbox
            parent: Parent widget

        Raises:
            ValueError: If max_val <= min_val or steps <= 0
        """
        super().__init__(parent)

        # Ensure opaque background to hide cell content during editing
        self.setAutoFillBackground(True)

        # Validate inputs
        if max_val <= min_val:
            raise ValueError(f"max_val ({max_val}) must be greater than min_val ({min_val})")
        if steps <= 0:
            raise ValueError(f"steps ({steps}) must be positive")

        # Store parameters
        self.min_val = min_val
        self.max_val = max_val
        self.steps = steps
        self.decimals = decimals

        # Create layout with minimal margins
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Create slider
        self.slider = QSlider(orientation, self)
        # Use normalized range [0, steps] for both int and float
        self.slider.setMinimum(0)
        self.slider.setMaximum(steps)

        # Create spinbox
        self.spinbox = QDoubleSpinBox(self)
        self.spinbox.setDecimals(decimals)
        self.spinbox.setSingleStep((max_val - min_val) / steps)
        self.spinbox.setRange(min_val, max_val)

        # Add widgets to layout
        layout.addWidget(self.slider, stretch=70)
        layout.addWidget(self.spinbox, stretch=30)

        # Connect signals for bidirectional synchronization
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

        # Set focus proxy to spinbox for keyboard navigation
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocusProxy(self.spinbox)

    def _on_slider_changed(self, slider_value):
        """Update spinbox when slider changes."""
        try:
            # Block signals to prevent infinite loop
            self.spinbox.blockSignals(True)

            # Use normalized mapping for both int and float
            normalized = slider_value / self.steps
            value = self.min_val + normalized * (self.max_val - self.min_val)

            self.spinbox.setValue(value)

        finally:
            self.spinbox.blockSignals(False)

    def _on_spinbox_changed(self, spinbox_value):
        """Update slider when spinbox changes."""
        try:
            # Block signals to prevent infinite loop
            self.slider.blockSignals(True)

            # Use normalized mapping for both int and float
            normalized = (spinbox_value - self.min_val) / (self.max_val - self.min_val)
            slider_pos = round(normalized * self.steps)  # Use round() for symmetric precision
            self.slider.setValue(slider_pos)
        finally:
            self.slider.blockSignals(False)

    def value(self):
        """Get current value from spinbox (source of truth).

        Returns:
            Current numeric value (int or float)
        """
        return self.spinbox.value()

    def setValue(self, value):
        """Set value, updating both slider and spinbox.

        Args:
            value: Numeric value to set
        """
        # Update spinbox (which will trigger _on_spinbox_changed to update slider)
        self.spinbox.setValue(float(value))


class PropertyDelegate(QStyledItemDelegate):
    """Custom delegate for property editors with different widget types.

    Supports multiple editor types:
    - string: QLineEdit with optional regex validation
    - int: QSpinBox with min/max range
    - float: QDoubleSpinBox with min/max range and decimal precision
    - bool: QCheckBox
    - enum: QComboBox with predefined choices
    - color: QColorDialog for hex color selection
    - slider: Composite widget with QSlider + QDoubleSpinBox for dual input

    Features:
    - Red background highlighting for validation errors
    - Gray/italic styling for read-only properties
    - Tooltip display of validation error messages
    """

    # Custom Qt roles
    EDITOR_TYPE_ROLE = Qt.ItemDataRole.UserRole + 1
    CALLBACK_ROLE = Qt.ItemDataRole.UserRole + 2
    VALIDATOR_ROLE = Qt.ItemDataRole.UserRole + 3
    VALIDATION_ERROR_ROLE = Qt.ItemDataRole.UserRole + 4
    MIN_VALUE_ROLE = Qt.ItemDataRole.UserRole + 5
    MAX_VALUE_ROLE = Qt.ItemDataRole.UserRole + 6
    CHOICES_ROLE = Qt.ItemDataRole.UserRole + 7
    READONLY_ROLE = Qt.ItemDataRole.UserRole + 8
    ADDRESS_ROLE = Qt.ItemDataRole.UserRole + 9
    ORIENTATION_ROLE = Qt.ItemDataRole.UserRole + 11
    STEP_ROLE = Qt.ItemDataRole.UserRole + 12

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        """Create appropriate editor widget based on item data.

        Args:
            parent: Parent widget
            option: Style options
            index: Model index of the item

        Returns:
            Editor widget or None if read-only or color type
        """
        # Only allow editing in column 1 (value column)
        if index.column() != 1:
            return None

        # Check if read-only
        if index.data(self.READONLY_ROLE):
            return None

        editor_type = index.data(self.EDITOR_TYPE_ROLE)

        if editor_type == "int":
            editor = QSpinBox(parent)
            min_val = index.data(self.MIN_VALUE_ROLE)
            max_val = index.data(self.MAX_VALUE_ROLE)
            if min_val is not None:
                editor.setMinimum(min_val)
            else:
                editor.setMinimum(-2147483648)  # Default int min
            if max_val is not None:
                editor.setMaximum(max_val)
            else:
                editor.setMaximum(2147483647)  # Default int max
            editor.setAutoFillBackground(True)
            return editor

        elif editor_type == "float":
            editor = QDoubleSpinBox(parent)
            min_val = index.data(self.MIN_VALUE_ROLE)
            max_val = index.data(self.MAX_VALUE_ROLE)
            decimals = index.data(Qt.ItemDataRole.UserRole + 10)  # DECIMALS_ROLE
            if min_val is not None:
                editor.setMinimum(min_val)
            else:
                editor.setMinimum(-1e308)  # Default float min
            if max_val is not None:
                editor.setMaximum(max_val)
            else:
                editor.setMaximum(1e308)  # Default float max
            if decimals is not None:
                editor.setDecimals(decimals)
            else:
                editor.setDecimals(2)  # Default 2 decimal places
            editor.setAutoFillBackground(True)
            return editor

        elif editor_type == "enum":
            editor = QComboBox(parent)
            choices = index.data(self.CHOICES_ROLE)
            if choices:
                editor.addItems(choices)
            editor.setAutoFillBackground(True)
            return editor

        elif editor_type == "bool":
            editor = QCheckBox(parent)
            editor.setAutoFillBackground(True)
            return editor

        elif editor_type == "slider":
            # Get parameters
            orientation = index.data(self.ORIENTATION_ROLE)
            if orientation is None:
                orientation = Qt.Orientation.Horizontal

            min_val = index.data(self.MIN_VALUE_ROLE)
            max_val = index.data(self.MAX_VALUE_ROLE)
            steps = index.data(self.STEP_ROLE) or 1000
            decimals = index.data(Qt.ItemDataRole.UserRole + 10) or 2  # DECIMALS_ROLE

            # Set defaults if not provided
            if min_val is None:
                min_val = 0.0
            if max_val is None:
                max_val = 1.0

            # Create composite widget
            editor = SliderLineEditWidget(
                min_val=min_val,
                max_val=max_val,
                steps=steps,
                orientation=orientation,
                decimals=decimals,
                parent=parent,
            )
            editor.setAutoFillBackground(True)
            return editor

        elif editor_type == "color":
            # Color handled via editorEvent (double-click opens dialog)
            return None

        elif editor_type == "string":
            editor = QLineEdit(parent)
            editor.setAutoFillBackground(True)
            return editor

        return super().createEditor(parent, option, index)

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        """Populate editor with current value.

        Args:
            editor: Editor widget
            index: Model index of the item
        """
        value = index.data(Qt.ItemDataRole.EditRole)

        if isinstance(editor, QSpinBox):
            try:
                editor.setValue(int(value) if value else 0)
            except (ValueError, TypeError):
                editor.setValue(0)
        elif isinstance(editor, QDoubleSpinBox):
            try:
                editor.setValue(float(value) if value else 0.0)
            except (ValueError, TypeError):
                editor.setValue(0.0)
        elif isinstance(editor, QComboBox):
            text = str(value) if value else ""
            index_pos = editor.findText(text)
            if index_pos >= 0:
                editor.setCurrentIndex(index_pos)
        elif isinstance(editor, QCheckBox):
            if isinstance(value, bool):
                editor.setChecked(value)
            elif isinstance(value, str):
                editor.setChecked(value.lower() in ("true", "1", "yes"))
            else:
                editor.setChecked(bool(value))
        elif isinstance(editor, SliderLineEditWidget):
            try:
                # Composite widget handles conversion internally
                editor.setValue(float(value) if value else editor.min_val)
            except (ValueError, TypeError):
                editor.setValue(editor.min_val)
        elif isinstance(editor, QLineEdit):
            editor.setText(str(value) if value else "")

    def setModelData(self, editor: QWidget, model, index: QModelIndex):
        """Save editor value back to model and run validation.

        Args:
            editor: Editor widget
            model: Data model
            index: Model index of the item
        """
        # Extract value from editor
        if isinstance(editor, QSpinBox):
            value = editor.value()
        elif isinstance(editor, QDoubleSpinBox):
            value = editor.value()
        elif isinstance(editor, QComboBox):
            value = editor.currentText()
        elif isinstance(editor, QCheckBox):
            value = editor.isChecked()
        elif isinstance(editor, SliderLineEditWidget):
            # Composite widget returns the correct type from spinbox
            value = editor.value()
        elif isinstance(editor, QLineEdit):
            value = editor.text()
        else:
            super().setModelData(editor, model, index)
            return

        # Run validator if present - validate BEFORE changing value
        validator = index.data(self.VALIDATOR_ROLE)
        self.parent().blockSignals(True)
        try:
            if callable(validator):
                error_msg = validator(value)
                if error_msg:  # Validation FAILED - don't update value
                    model.setData(index, error_msg, self.VALIDATION_ERROR_ROLE)
                    # Set tooltip to show error
                    item = model.itemFromIndex(index) if hasattr(model, "itemFromIndex") else None
                    if item:
                        item.setToolTip(1, error_msg)
                    return  # Exit early - keep old value
                else:  # Validation PASSED - clear error state
                    model.setData(index, "", self.VALIDATION_ERROR_ROLE)
                    item = model.itemFromIndex(index) if hasattr(model, "itemFromIndex") else None
                    if item:
                        item.setToolTip(1, "")

            # Only set value if no validator OR validation passed
            model.setData(index, value, Qt.ItemDataRole.EditRole)
        finally:
            self.parent().blockSignals(False)

    def _paint_color_cell(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        """Custom paint for color cells with colored box preview.
        
        Args:
            painter: QPainter instance
            option: Style options
            index: Model index of the item
        """
        painter.save()
        
        try:
            # Get cell rectangle
            cell_rect = option.rect
            
            # Draw selection background if selected
            if option.state & option.state.State_Selected:
                painter.fillRect(cell_rect, option.palette.highlight())
            
            # Check for validation error - draw red background
            error_msg = index.data(self.VALIDATION_ERROR_ROLE)
            if error_msg:
                painter.fillRect(cell_rect, QColor(255, 200, 200))
            
            # Get color value
            color_value = index.data(Qt.ItemDataRole.DisplayRole)
            color = QColor(color_value) if color_value and QColor(color_value).isValid() else QColor(Qt.GlobalColor.white)
            
            # Calculate color box rectangle (left-aligned with margins)
            box_size = cell_rect.height() - 4  # 2px margin top/bottom
            box_rect = QRect(
                cell_rect.left() + 2,  # 2px left margin
                cell_rect.top() + 2,   # 2px top margin
                box_size,
                box_size
            )
            
            # Draw colored box
            painter.fillRect(box_rect, color)
            
            # Draw black border around box
            painter.setPen(QColor(0, 0, 0))
            painter.drawRect(box_rect)
            
            # Calculate text rectangle (to the right of the box)
            text_rect = QRect(
                box_rect.right() + 4,  # 4px spacing after box
                cell_rect.top(),
                cell_rect.width() - box_size - 6,  # Account for margins
                cell_rect.height()
            )
            
            # Set text color (gray for read-only)
            readonly = index.data(self.READONLY_ROLE)
            if readonly:
                text_color = QColor(128, 128, 128)
                font = option.font
                font.setItalic(True)
                painter.setFont(font)
            elif option.state & option.state.State_Selected:
                text_color = option.palette.highlightedText().color()
            else:
                text_color = option.palette.text().color()
            
            painter.setPen(text_color)
            
            # Draw text
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, str(color_value) if color_value else "")
            
        finally:
            painter.restore()

    def paint(self, painter, option: QStyleOptionViewItem, index: QModelIndex):
        """Custom paint to show validation errors and read-only styling.

        Args:
            painter: QPainter instance
            option: Style options
            index: Model index of the item
        """
        # Check if this is a color cell - use custom painting
        editor_type = index.data(self.EDITOR_TYPE_ROLE)
        if editor_type == "color" and index.column() == 1:
            self._paint_color_cell(painter, option, index)
            return
        
        # For all other cells, use existing logic
        # Check for validation error
        error_msg = index.data(self.VALIDATION_ERROR_ROLE)

        # Check if read-only
        readonly = index.data(self.READONLY_ROLE)

        # Modify style option
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)

        if error_msg:
            # Red background for validation errors
            opt.backgroundBrush = QColor(255, 200, 200)

        if readonly:
            # Gray/italic for read-only properties
            opt.palette.setColor(QPalette.Text, QColor(128, 128, 128))
            font = opt.font
            font.setItalic(True)
            opt.font = font

        # Call parent paint with modified option
        super().paint(painter, opt, index)

    def editorEvent(self, event, model, option: QStyleOptionViewItem, index: QModelIndex) -> bool:
        """Handle color picker dialog for color type properties.

        Args:
            event: Qt event
            model: Data model
            option: Style options
            index: Model index of the item

        Returns:
            True if event was handled
        """
        editor_type = index.data(self.EDITOR_TYPE_ROLE)

        if editor_type == "color" and event.type() == QEvent.MouseButtonDblClick:
            # Get current color value
            current_value = index.data(Qt.ItemDataRole.EditRole)
            current_color = QColor(current_value) if current_value else QColor(Qt.GlobalColor.white)

            # Open color dialog
            color = QColorDialog.getColor(current_color, option.widget)

            if color.isValid():
                # Convert to hex string
                hex_color = color.name()  # Returns #RRGGBB format

                # Run validator if present - validate BEFORE changing value
                validator = index.data(self.VALIDATOR_ROLE)
                if callable(validator):
                    error_msg = validator(hex_color)
                    if error_msg:  # Validation FAILED - don't update value
                        model.setData(index, error_msg, self.VALIDATION_ERROR_ROLE)
                        item = model.itemFromIndex(index) if hasattr(model, "itemFromIndex") else None
                        if item:
                            item.setToolTip(1, error_msg)
                        return True  # Consume event but don't change value
                    else:  # Validation PASSED - clear error state
                        model.setData(index, "", self.VALIDATION_ERROR_ROLE)
                        item = model.itemFromIndex(index) if hasattr(model, "itemFromIndex") else None
                        if item:
                            item.setToolTip(1, "")

                # Only set value if no validator OR validation passed
                model.setData(index, hex_color, Qt.ItemDataRole.EditRole)
                return True

        return super().editorEvent(event, model, option, index)
