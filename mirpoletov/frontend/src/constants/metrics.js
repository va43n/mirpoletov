export const METRICS_DICTIONARY = {
    "flights": {
        name: "Число полетов",
        description: "Число полетов в регионе",
        id: "flights",
    },
    "mean_duration": {
        name: "Средняя длительность",
        description: "Средняя длительность полета",
        id: "mean_duration",
    },
    "top_regs": {
        name: "Топ регионов",
        description: "Убывающий список регионов по числу полетов",
        id: "top_regs",
    },
    "peak_load": {
        name: "Пиковая нагрузка",
        description: "Максимальное число полетов за час",
        id: "peak_load",
    },
    "mean_dynamic": {
        name: "Среднесуточная динамика",
        description: "Среднее и медианное число полетов в сутки",
        id: "mean_dynamic",
    },
    "rise_fall": {
        name: "Рост/падение",
        description: "Процентное изменение числа полетов за месяц",
        id: "rise_fall",
    },
    // "flight_density": {
    //     name: "Flight Density",
    //     description: "Число полетов на 1000 км² территории региона",
    //     id: "flight_density",
    // },
    "day_act": {
        name: "Дневная активность",
        description: "Распределение полетов по часам",
        id: "day_act",
    },
    "empty_days": {
        name: "Нулевые дни",
        description: "Количество дней без полетов по субъекту",
        id: "empty_days",
    }
}