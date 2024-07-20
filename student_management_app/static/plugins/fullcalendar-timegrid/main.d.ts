




declare module '@fullcalendar/timegrid' {
    import AbstractTimeGridView from '@fullcalendar/timegrid/AbstractTimeGridView';
    import TimeGridView, { buildDayTable } from '@fullcalendar/timegrid/TimeGridView';
    import { TimeGridSeg } from '@fullcalendar/timegrid/TimeGrid';
    import { TimeGridSlicer, buildDayRanges } from '@fullcalendar/timegrid/SimpleTimeGrid';
    export { TimeGridView, AbstractTimeGridView, buildDayTable, buildDayRanges, TimeGridSlicer, TimeGridSeg };
    export { default as TimeGrid } from '@fullcalendar/timegrid/TimeGrid';
    const _default: import("@fullcalendar/core").PluginDef;
    export default _default;
}

declare module '@fullcalendar/timegrid/AbstractTimeGridView' {
    import { ScrollComponent, View, ViewSpec, DateProfileGenerator, ComponentContext, Duration } from '@fullcalendar/core';
    import { DayGrid } from '@fullcalendar/daygrid';
    import TimeGrid from '@fullcalendar/timegrid/TimeGrid';
    import AllDaySplitter from '@fullcalendar/timegrid/AllDaySplitter';
    export { TimeGridView as default, TimeGridView };
    abstract class TimeGridView extends View {
        timeGrid: TimeGrid;
        dayGrid: DayGrid;
        scroller: ScrollComponent;
        axisWidth: any;
        protected splitter: AllDaySplitter;
        constructor(context: ComponentContext, viewSpec: ViewSpec, dateProfileGenerator: DateProfileGenerator, parentEl: HTMLElement);
        destroy(): void;
        renderSkeletonHtml(): string;
        getNowIndicatorUnit(): string;
        unrenderNowIndicator(): void;
        updateSize(isResize: boolean, viewHeight: number, isAuto: boolean): void;
        updateBaseSize(isResize: any, viewHeight: any, isAuto: any): void;
        computeScrollerHeight(viewHeight: any): number;
        computeDateScroll(duration: Duration): {
            top: any;
        };
        queryDateScroll(): {
            top: number;
        };
        applyDateScroll(scroll: any): void;
        renderHeadIntroHtml: () => string;
        axisStyleAttr(): string;
        renderTimeGridBgIntroHtml: () => string;
        renderTimeGridIntroHtml: () => string;
        renderDayGridBgIntroHtml: () => string;
        renderDayGridIntroHtml: () => string;
    }
}

declare module '@fullcalendar/timegrid/TimeGridView' {
    import { DateProfileGenerator, DateProfile, ComponentContext, ViewSpec, DayHeader, DayTable, ViewProps } from '@fullcalendar/core';
    import { SimpleDayGrid } from '@fullcalendar/daygrid';
    import SimpleTimeGrid from '@fullcalendar/timegrid/SimpleTimeGrid';
    import AbstractTimeGridView from '@fullcalendar/timegrid/AbstractTimeGridView';
    export { TimeGridView as default, TimeGridView };
    class TimeGridView extends AbstractTimeGridView {
        header: DayHeader;
        simpleDayGrid: SimpleDayGrid;
        simpleTimeGrid: SimpleTimeGrid;
        constructor(_context: ComponentContext, viewSpec: ViewSpec, dateProfileGenerator: DateProfileGenerator, parentEl: HTMLElement);
        destroy(): void;
        render(props: ViewProps): void;
        renderNowIndicator(date: any): void;
    }
    export function buildDayTable(dateProfile: DateProfile, dateProfileGenerator: DateProfileGenerator): DayTable;
}

declare module '@fullcalendar/timegrid/TimeGrid' {
    import { PositionCache, Duration, DateMarker, DateFormatter, ComponentContext, DateComponent, Seg, EventSegUiInteractionState, DateProfile } from '@fullcalendar/core';
    export interface RenderProps {
        renderBgIntroHtml: () => string;
        renderIntroHtml: () => string;
    }
    export interface TimeGridSeg extends Seg {
        col: number;
        start: DateMarker;
        end: DateMarker;
    }
    export interface TimeGridCell {
        date: DateMarker;
        htmlAttrs?: string;
    }
    export interface TimeGridProps {
        dateProfile: DateProfile;
        cells: TimeGridCell[];
        businessHourSegs: TimeGridSeg[];
        bgEventSegs: TimeGridSeg[];
        fgEventSegs: TimeGridSeg[];
        dateSelectionSegs: TimeGridSeg[];
        eventSelection: string;
        eventDrag: EventSegUiInteractionState | null;
        eventResize: EventSegUiInteractionState | null;
    }
    export { TimeGrid as default, TimeGrid };
    class TimeGrid extends DateComponent<TimeGridProps> {
        renderProps: RenderProps;
        slotDuration: Duration;
        snapDuration: Duration;
        snapsPerSlot: any;
        labelFormat: DateFormatter;
        labelInterval: Duration;
        colCnt: number;
        colEls: HTMLElement[];
        slatContainerEl: HTMLElement;
        slatEls: HTMLElement[];
        nowIndicatorEls: HTMLElement[];
        colPositions: PositionCache;
        slatPositions: PositionCache;
        isSlatSizesDirty: boolean;
        isColSizesDirty: boolean;
        rootBgContainerEl: HTMLElement;
        bottomRuleEl: HTMLElement;
        contentSkeletonEl: HTMLElement;
        colContainerEls: HTMLElement[];
        fgContainerEls: HTMLElement[];
        bgContainerEls: HTMLElement[];
        mirrorContainerEls: HTMLElement[];
        highlightContainerEls: HTMLElement[];
        businessContainerEls: HTMLElement[];
        constructor(context: ComponentContext, el: HTMLElement, renderProps: RenderProps);
        processOptions(): void;
        computeLabelInterval(slotDuration: any): any;
        render(props: TimeGridProps): void;
        destroy(): void;
        updateSize(isResize: boolean): void;
        _renderSlats(dateProfile: DateProfile): void;
        renderSlatRowHtml(dateProfile: DateProfile): string;
        _renderColumns(cells: TimeGridCell[], dateProfile: DateProfile): void;
        _unrenderColumns(): void;
        renderContentSkeleton(): void;
        unrenderContentSkeleton(): void;
        groupSegsByCol(segs: any): any[];
        attachSegsByCol(segsByCol: any, containerEls: HTMLElement[]): void;
        getNowIndicatorUnit(): string;
        renderNowIndicator(segs: TimeGridSeg[], date: any): void;
        unrenderNowIndicator(): void;
        getTotalSlatHeight(): number;
        computeDateTop(when: DateMarker, startOfDayDate?: DateMarker): any;
        computeTimeTop(duration: Duration): any;
        computeSegVerticals(segs: any): void;
        assignSegVerticals(segs: any): void;
        generateSegVerticalCss(seg: any): {
            top: any;
            bottom: number;
        };
        buildPositionCaches(): void;
        buildColPositions(): void;
        buildSlatPositions(): void;
        positionToHit(positionLeft: any, positionTop: any): {
            col: any;
            dateSpan: {
                range: {
                    start: Date;
                    end: Date;
                };
                allDay: boolean;
            };
            dayEl: HTMLElement;
            relativeRect: {
                left: any;
                right: any;
                top: any;
                bottom: any;
            };
        };
        _renderEventDrag(state: EventSegUiInteractionState): void;
        _unrenderEventDrag(state: EventSegUiInteractionState): void;
        _renderEventResize(state: EventSegUiInteractionState): void;
        _unrenderEventResize(state: EventSegUiInteractionState): void;
        _renderDateSelection(segs: Seg[]): void;
        _unrenderDateSelection(segs: Seg[]): void;
    }
}

declare module '@fullcalendar/timegrid/SimpleTimeGrid' {
    import { DateComponent, DateProfile, EventStore, EventUiHash, EventInteractionState, DateSpan, DateRange, DayTable, DateEnv, DateMarker, Slicer, Hit, ComponentContext } from '@fullcalendar/core';
    import TimeGrid, { TimeGridSeg } from '@fullcalendar/timegrid/TimeGrid';
    export interface SimpleTimeGridProps {
        dateProfile: DateProfile | null;
        dayTable: DayTable;
        businessHours: EventStore;
        eventStore: EventStore;
        eventUiBases: EventUiHash;
        dateSelection: DateSpan | null;
        eventSelection: string;
        eventDrag: EventInteractionState | null;
        eventResize: EventInteractionState | null;
    }
    export { SimpleTimeGrid as default, SimpleTimeGrid };
    class SimpleTimeGrid extends DateComponent<SimpleTimeGridProps> {
        timeGrid: TimeGrid;
        constructor(context: ComponentContext, timeGrid: TimeGrid);
        destroy(): void;
        render(props: SimpleTimeGridProps): void;
        renderNowIndicator(date: DateMarker): void;
        buildPositionCaches(): void;
        queryHit(positionLeft: number, positionTop: number): Hit;
    }
    export function buildDayRanges(dayTable: DayTable, dateProfile: DateProfile, dateEnv: DateEnv): DateRange[];
    export class TimeGridSlicer extends Slicer<TimeGridSeg, [DateRange[]]> {
        sliceRange(range: DateRange, dayRanges: DateRange[]): TimeGridSeg[];
    }
}

declare module '@fullcalendar/timegrid/AllDaySplitter' {
    import { Splitter, EventDef, DateSpan } from '@fullcalendar/core';
    export { AllDaySplitter as default, AllDaySplitter };
    class AllDaySplitter extends Splitter {
        getKeyInfo(): {
            allDay: {};
            timed: {};
        };
        getKeysForDateSpan(dateSpan: DateSpan): string[];
        getKeysForEventDef(eventDef: EventDef): string[];
    }
}

