const { createApp } = Vue

// Taken from https://stackoverflow.com/a/29774197.
function getDateFormatted(date) {
    const offset = date.getTimezoneOffset()
    date = new Date(date.getTime() - (offset * 60 * 1000))
    return date.toISOString().split('T')[0]
}

scriptData = JSON.parse(document.getElementById('script_data').textContent)

createApp({
    data() {
        return { startDate: new Date(scriptData.start_date), endDate: new Date(scriptData.end_date), overRange: scriptData.start_date != scriptData.end_date }
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
