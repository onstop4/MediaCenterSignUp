const { createApp } = Vue

function getDateFromScriptData(s) {
    return new Date(s.includes("T") ? s : s + "T00:00:00")
}

function getDateFormatted(date) {
    return date.toISOString().split('T')[0]
}

scriptData = JSON.parse(document.getElementById('script_data').textContent)

createApp({
    data() {
        return { startDate: getDateFromScriptData(scriptData.start_date), endDate: getDateFromScriptData(scriptData.end_date), overRange: scriptData.start_date != scriptData.end_date }
    },
    computed: {
        startDateValue: {
            get() {
                return getDateFormatted(this.startDate)
            },
            set(dateString) {
                let [year, month, day] = dateString.split('-')
                this.startDate = new Date(year, month - 1, day)
            }
        },
        endDateValue: {
            get() {
                return getDateFormatted(this.endDate)
            },
            set(dateString) {
                let [year, month, day] = dateString.split('-')
                this.endDate = new Date(year, month - 1, day)
            }
        }
    }
}).mount('#app')
